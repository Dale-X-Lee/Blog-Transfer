# test_manual.py
import tempfile, datetime as dt
from pathlib import Path

# 把 file_processor.py（含 FileProcessor & PDFHandler）放到同目录或 PYTHONPATH
import file_processor as fp

def test_md_pipeline():
    with tempfile.TemporaryDirectory() as tmp:
        md_path = Path(tmp) / 'hello world.md'
        md_path.write_text('# Hello 世界\n\n公式 $E=mc^2$\n\n$$\nx^2 + y^2 = 1\n$$',
                           encoding='utf-8')
        print('md文件位置',md_path)

        meta = {
            'title': '测试 标题',       # 含空格
            'description': '手动测试',
            'tags': ['test', '公式']
        }
        out_dir = Path(tmp) / 'out'
        new_file = fp.FileProcessor.process_file(str(md_path), str(out_dir), meta)

        print('>>> 生成的 md 文件：', new_file)
        print('--- 内容 ---')
        print(Path(new_file).read_text(encoding='utf-8'))

def test_pdf_pipeline():
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = Path(tmp) / 'demo file.pdf'
        pdf_path.write_bytes(b'%PDF-1.4\n%%EOF')   # 最小有效 PDF
        print('pdf位置',pdf_path)

        meta = {'title': 'PDF 测试', 'description': 'pdf 描述'}
        out_dir = Path(tmp) / 'out'
        new_file = fp.FileProcessor.process_file(str(pdf_path), str(out_dir), meta)

        print('>>> 生成的重定向 md 文件：', new_file)
        print('--- 内容 ---')
        print(Path(new_file).read_text(encoding='utf-8'))

        # 确认 PDF 已被复制
        assets = Path('../assets/pdf/posts').resolve()
        copied = list(assets.glob('demo file*.pdf'))
        print('>>> PDF 复制结果：', copied)

if __name__ == '__main__':
    test_md_pipeline()
    print('='*60)
    test_pdf_pipeline()