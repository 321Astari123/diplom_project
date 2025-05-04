import os
import zipfile
import xml.etree.ElementTree as ET
from lxml import etree
from ebooklib import epub
from PIL import Image
import io
import base64
import logging
import re

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BookParser:
    def __init__(self):
        self.cover_dir = os.path.join('static', 'uploads', 'covers')
        os.makedirs(self.cover_dir, exist_ok=True)
        logger.debug(f"Инициализация BookParser. Директория для обложек: {self.cover_dir}")
        
    def is_valid_epub(self, file_path):
        """Проверяет, является ли файл корректным EPUB"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # Проверяем наличие обязательных файлов
                required_files = ['mimetype', 'META-INF/container.xml']
                for file in required_files:
                    if file not in zf.namelist():
                        logger.error(f"Отсутствует обязательный файл в EPUB: {file}")
                        return False
                
                # Проверяем mimetype
                with zf.open('mimetype') as f:
                    mimetype = f.read().decode('utf-8').strip()
                    if mimetype != 'application/epub+zip':
                        logger.error(f"Неверный mimetype: {mimetype}")
                        return False
                
                return True
        except zipfile.BadZipFile:
            logger.error("Файл не является корректным ZIP-архивом")
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке EPUB: {str(e)}")
            return False
            
    def parse_book(self, file_path):
        """Парсит содержимое книги в зависимости от формата"""
        logger.debug(f"Начало парсинга книги: {file_path}")
        if file_path.lower().endswith('.fb2'):
            return self.parse_fb2(file_path)
        elif file_path.lower().endswith('.epub'):
            if not self.is_valid_epub(file_path):
                raise ValueError('Файл не является корректным EPUB')
            return self.parse_epub(file_path)
        else:
            raise ValueError('Неподдерживаемый формат файла')
            
    def parse_metadata(self, file_path):
        """Парсит метаданные книги"""
        try:
            file_type = os.path.splitext(file_path)[1].lower()
            if file_type == '.fb2':
                return self._parse_fb2_metadata(file_path)
            elif file_type == '.epub':
                return self._parse_epub_metadata(file_path)
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file_type}")
        except Exception as e:
            logger.error(f"Ошибка при парсинге метаданных: {str(e)}")
            raise

    def _parse_fb2_metadata(self, file_path):
        """Парсит метаданные из FB2 файла"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            # Декодируем содержимое
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                content = content.decode('windows-1251')
                
            # Извлекаем метаданные
            title = re.search(r'<title-info>.*?<book-title>(.*?)</book-title>', content, re.DOTALL)
            author = re.search(r'<title-info>.*?<author>.*?<first-name>(.*?)</first-name>.*?<last-name>(.*?)</last-name>', content, re.DOTALL)
            genre = re.search(r'<title-info>.*?<genre>(.*?)</genre>', content, re.DOTALL)
            cover = re.search(r'<coverpage>.*?<image.*?href="#(.*?)".*?>', content, re.DOTALL)
            
            # Обрабатываем результаты
            title = title.group(1).strip() if title else 'Без названия'
            author = f"{author.group(1).strip()} {author.group(2).strip()}" if author else 'Неизвестный автор'
            genre = genre.group(1).strip() if genre else None
            cover_id = cover.group(1) if cover else None
            
            # Ищем обложку в бинарных данных
            cover_data = None
            if cover_id:
                cover_match = re.search(rf'<binary id="{cover_id}".*?>(.*?)</binary>', content, re.DOTALL)
                if cover_match:
                    cover_data = base64.b64decode(cover_match.group(1))
                    
            logger.debug(f"Извлечены метаданные FB2: title={title}, author={author}, genre={genre}")
            return {
                'title': title,
                'author': author,
                'genre': genre,
                'cover': cover_data
            }
        except Exception as e:
            logger.error(f"Ошибка при парсинге метаданных FB2: {str(e)}")
            raise

    def _parse_epub_metadata(self, file_path):
        """Парсит метаданные из EPUB файла"""
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                # Ищем файл с метаданными
                metadata_file = None
                for name in z.namelist():
                    if name.endswith('content.opf'):
                        metadata_file = name
                        break
                        
                if not metadata_file:
                    raise ValueError("Не найден файл с метаданными в EPUB")
                    
                # Читаем метаданные
                content = z.read(metadata_file).decode('utf-8')
                
                # Извлекаем метаданные
                title = re.search(r'<dc:title>(.*?)</dc:title>', content)
                author = re.search(r'<dc:creator>(.*?)</dc:creator>', content)
                genre = re.search(r'<dc:subject>(.*?)</dc:subject>', content)
                cover_id = re.search(r'<meta name="cover" content="(.*?)"/>', content)
                
                # Обрабатываем результаты
                title = title.group(1).strip() if title else 'Без названия'
                author = author.group(1).strip() if author else 'Неизвестный автор'
                genre = genre.group(1).strip() if genre else None
                cover_id = cover_id.group(1) if cover_id else None
                
                # Ищем обложку
                cover_data = None
                if cover_id:
                    # Ищем путь к обложке
                    cover_path = None
                    for name in z.namelist():
                        if name.endswith(cover_id):
                            cover_path = name
                            break
                            
                    if cover_path:
                        cover_data = z.read(cover_path)
                        
                logger.debug(f"Извлечены метаданные EPUB: title={title}, author={author}, genre={genre}")
                return {
                    'title': title,
                    'author': author,
                    'genre': genre,
                    'cover': cover_data
                }
        except Exception as e:
            logger.error(f"Ошибка при парсинге метаданных EPUB: {str(e)}")
            raise
            
    def parse_fb2(self, file_path):
        """Парсит FB2 файл и возвращает текст"""
        try:
            logger.debug(f"Парсинг FB2 файла: {file_path}")
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            # Получаем текст из body
            body = root.find('.//{http://www.gribuser.ru/xml/fictionbook/2.0}body')
            if body is None:
                raise ValueError('Не удалось найти содержимое книги')
                
            text = []
            section_count = 0
            paragraph_count = 0
            
            for section in body.findall('.//{http://www.gribuser.ru/xml/fictionbook/2.0}section'):
                section_count += 1
                for p in section.findall('.//{http://www.gribuser.ru/xml/fictionbook/2.0}p'):
                    paragraph_count += 1
                    if p.text is not None:
                        text.append(p.text)
                    else:
                        logger.debug(f"Найден пустой параграф в секции {section_count}, параграф {paragraph_count}")
                        text.append('')
                    
            logger.debug(f"Успешно распарсен FB2 файл: {file_path}")
            logger.debug(f"Найдено секций: {section_count}, параграфов: {paragraph_count}")
            return '\n\n'.join(text)
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге FB2 файла {file_path}: {str(e)}")
            raise ValueError(f'Ошибка при парсинге FB2 файла: {str(e)}')
            
    def parse_epub(self, file_path):
        """Парсит EPUB файл и возвращает текст"""
        try:
            logger.debug(f"Парсинг EPUB файла: {file_path}")
            book = epub.read_epub(file_path)
            text = []
            
            # Получаем текст из всех документов
            for item in book.get_items():
                if item.get_type() == epub.ITEM_DOCUMENT:
                    content = item.get_content().decode('utf-8')
                    text.append(content)
                    
            logger.debug(f"Успешно распарсен EPUB файл: {file_path}")
            return '\n\n'.join(text)
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге EPUB файла {file_path}: {str(e)}")
            raise ValueError(f'Ошибка при парсинге EPUB файла: {str(e)}')
            
    def save_cover(self, cover_data, cover_path):
        """Сохраняет обложку книги"""
        try:
            logger.debug(f"Сохранение обложки для книги: {cover_path}")
            if not cover_data:
                logger.warning("Нет данных обложки для сохранения")
                return ''
            # Генерируем имя файла
            # cover_path уже содержит полный путь
            # Сохраняем изображение
            if isinstance(cover_data, bytes):
                img = Image.open(io.BytesIO(cover_data))
            elif isinstance(cover_data, str):
                try:
                    img = Image.open(io.BytesIO(base64.b64decode(cover_data)))
                except Exception as e:
                    logger.error(f"Ошибка при декодировании base64: {str(e)}")
                    return ''
            else:
                logger.error(f"Неподдерживаемый тип данных обложки: {type(cover_data)}")
                return ''
            img.save(cover_path)
            logger.debug(f"Обложка успешно сохранена: {cover_path}")
            return os.path.basename(cover_path)
        except Exception as e:
            logger.error(f"Ошибка при сохранении обложки для {cover_path}: {str(e)}")
            return ''  # Возвращаем пустую строку вместо вызова исключения 