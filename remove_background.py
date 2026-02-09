#!/usr/bin/env python3
"""
Скрипт для удаления фонов с изображений
Автор: Isabek
Использует библиотеку rembg для удаления фонов с изображений
"""

import os
import argparse
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Проверяем наличие необходимых библиотек
try:
    from rembg import remove
    from PIL import Image
except ImportError:
    print("Необходимые пакеты не найдены. Устанавливаем...")
    os.system("pip install rembg pillow")
    from rembg import remove
    from PIL import Image


def remove_background(input_path, output_path=None, model='u2net'):
    """
    Удаляет фон с изображения
    
    Args:
        input_path (str): Путь к входному изображению
        output_path (str): Путь для сохранения выходного изображения (необязательно)
        model (str): Модель для использования ('u2net', 'u2netp', 'u2net_human_seg', 'silueta', 'isnet-general-use')
    """
    try:
        # Открываем входное изображение
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()
        
        # Удаляем фон
        output_data = remove(input_data, model_name=model)
        
        # Генерируем путь для выходного файла если не указан
        if output_path is None:
            input_file = Path(input_path)
            output_path = input_file.parent / f"{input_file.stem}_no_bg.png"
        
        # Сохраняем выходное изображение
        with open(output_path, 'wb') as output_file:
            output_file.write(output_data)
        
        print(f"✓ Фон успешно удалён!")
        print(f"  Вход: {input_path}")
        print(f"  Выход: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"✗ Ошибка при удалении фона: {str(e)}")
        return None


def batch_remove_background(input_dir, output_dir=None, model='u2net'):
    """
    Удаляет фоны со всех изображений в директории
    
    Args:
        input_dir (str): Директория с входными изображениями
        output_dir (str): Директория для сохранения выходных изображений (необязательно)
        model (str): Модель для удаления фона
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"✗ Входная директория не существует: {input_dir}")
        return
    
    # Создаём выходную директорию если не указана
    if output_dir is None:
        output_dir = input_path.parent / f"{input_path.name}_no_bg"
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Поддерживаемые форматы изображений
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # Обрабатываем все изображения
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(f"*{ext}"))
        image_files.extend(input_path.glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"✗ Изображения не найдены в директории: {input_dir}")
        return
    
    print(f"Обрабатываем {len(image_files)} изображений...")
    
    success_count = 0
    for i, image_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Обработка: {image_file.name}")
        
        output_file = output_path / f"{image_file.stem}_no_bg.png"
        
        if remove_background(str(image_file), str(output_file), model):
            success_count += 1
    
    print(f"\n✓ Пакетная обработка завершена!")
    print(f"  Успешно обработано: {success_count}/{len(image_files)} изображений")
    print(f"  Выходная директория: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Удаление фонов с изображений",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Удалить фон с одного изображения
  python remove_background.py input.jpg
  
  # Указать выходной файл
  python remove_background.py input.jpg -o output.png
  
  # Обработать всю директорию
  python remove_background.py -d /path/to/images
  
  # Использовать другую модель
  python remove_background.py input.jpg -m u2net_human_seg
  
Доступные модели:
  - u2net: Универсальная (по умолчанию)
  - u2netp: Облегчённая версия
  - u2net_human_seg: Для сегментации людей
  - silueta: Для силуэтов
  - isnet-general-use: Высокого качества универсальная
        """
    )
    
    parser.add_argument('input', nargs='?', help='Входной файл изображения')
    parser.add_argument('-o', '--output', help='Выходной файл изображения')
    parser.add_argument('-d', '--directory', help='Обработать все изображения в директории')
    parser.add_argument('-od', '--output-dir', help='Выходная директория для пакетной обработки')
    parser.add_argument('-m', '--model', default='u2net',
                       choices=['u2net', 'u2netp', 'u2net_human_seg', 'silueta', 'isnet-general-use'],
                       help='Модель для удаления фона')
    
    args = parser.parse_args()
    
    if args.directory:
        # Режим пакетной обработки
        batch_remove_background(args.directory, args.output_dir, args.model)
    elif args.input:
        # Режим одного изображения
        remove_background(args.input, args.output, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
