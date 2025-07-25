import re
from config import standard_output_style


class MathJax_Converter:
    """
    MathJax_Converter 类说明

    功能概述:
    将 LaTeX 数学公式转换为自定义 MathJax 格式，特性包括：
    1. 公式格式标准化: 处理行内公式 ($...$ / \\(...\\)) 和块级公式 ($$...$$ / equation* 环境)
    2. Markdown 兼容: 转义数学公式中的特殊字符 (如 | → \\vert)
    3. 格式优化: 合并连续空行，保留引用层级 (> 符号)

    初始化参数:
    - mode (str): 预留扩展参数，默认 'md'
    - output_style (dict): 公式包围符号配置，默认:
        {
            'math_inline_surrounding': '$$',
            'math_block_begin': '$$',
            'math_block_end': '$$\n'
        }

    方法说明:
    1. convert(input_text: str) -> str
    主入口方法，处理流程:
    块级公式转换 → 空行合并 → 行内公式转换

    2. _convert_block_math(text)
    处理块级公式，支持:
    - 环境: \\begin{equation*}, \\[
    - 分隔符: $$$$, $$$$$
    保留引用层级 (> 符号)，自动添加配置的包围符

    3. _convert_inline_math(text)
    处理行内公式语法:
    - \\(...\\) → 配置的包围符
    - $...$ (非连续$符号) → 配置的包围符

    4. _sanitize_special_chars(text)
    冲突字符处理:
    - | 转换为 \\vert
    - _/^ 后接非空格字符时添加花括号 (如 x^2 → x^{2})
    - 合并多个空格为单个

    5. _merge_consecutive_empty_lines(text)
    智能空行合并:
    - 保留不同层级的引用空行 (> > >)
    - 普通空行最多保留一个

    使用示例:
    >>> converter = MathJax_Converter()
    >>> input_text = '''
    > 公式块:
    > $$
    > x = \\sqrt{b_0^2}
    > $$
    行内公式: $E=mc^2$
    '''
    >>> print(converter.convert(input_text))
    > 公式块:
    > 
    > $$
    > x = \\sqrt{b_{0}^{2}}
    > $$
    行内公式: $$E=mc^{2}$$

    注意事项:
    1. 公式内容包含未转义 $ 或 \\ 可能导致匹配错误
    2. _/^ 符号会被自动包裹 (如 a_b → a_{b})
    3. mode 参数当前版本未实际使用
    """
    def __init__(self,mode:str='md',output_style=standard_output_style):
        self.mode = mode
        self.style = output_style
        return

    def convert(self, input_text: str) -> str:
        """
        主转换入口：处理文本中所有数学环境

        :param input_text: 原始文本（包含 LaTeX 公式）
        :return: MathJax 兼容的 Markdown 文本
        """
        # text = self._convert_custom_environments(input_text) # 此行代码供转化LaTeX使用
        text = self._convert_block_math(input_text)
        text = MathJax_Converter._merge_consecutive_empty_lines(text)
        text = self._convert_inline_math(text)
        return text

    def _convert_inline_math(self, text: str) -> str:
        """转换行内公式（如 \(...\) 或 $...$）"""
        # 处理\(...\)格式
        text = re.sub(
            r'(?<!\\)\\\((.*?)(?<!\\)\\\)',
            lambda m: f'{self.style["math_inline_surrounding"]}%s{self.style["math_inline_surrounding"]}' % self._sanitize_special_chars(m.group(1)),
            text,
            flags=re.DOTALL
        )
        
        # 处理$...$格式（排除转义情况）
        text = re.sub(
            r'(?<!\\)\$(?!\s)([^$]+?)(?<!\s)\$(?!\$)',
            lambda m: f'{self.style["math_inline_surrounding"]}%s{self.style["math_inline_surrounding"]}' % self._sanitize_special_chars(m.group(1)),
            text,
            flags=re.DOTALL
        )
        
        return text

    def _convert_block_math(self, text: str) -> str:
        """转换块级数学公式，保留引用层级并处理格式"""
        # 匹配包含换行的块公式结构（兼容引用环境和常规环境）
        block_pattern = re.compile(
            r'''
            (^[>]*)                # 捕获可能的引用符号(包含多级>)-group 1
            \s*                    # 可能的空格
            (\\begin\{equation\*\}|\\\[|\$\$|\$\$\$)  # 开始标记-group 2
            (.*?)                  # 公式内容（非贪婪）-group 3
            (\\end\{equation\*\}|\\\]|\$\$|\$\$\$)    # 结束标记-group 4
            \s*                    # 可能的空格
            (                      # 捕获后续可能的换行符
            (?:\n|$)               # 匹配换行或文本结束
            )
            ''', 
            re.DOTALL | re.MULTILINE | re.VERBOSE
        )

        def _replace_block(match):
            indent = match.group(1).strip()       # 保留原有的引用符号 >
            content = match.group(3) #.strip()
            trailing_newline = match.group(5)
            space = ' ' if indent else ''

            # 清洗公式内容
            sanitized = self._sanitize_special_chars(content)
            
            # 构造符合MathJax规范的块公式
            new_block = (
                f"{indent}\n{indent}{space}{self.style['math_block_begin']}"
                f"{sanitized}"
                f"{self.style['math_block_end']}{indent}"
            )
            
            # 规范化换行符（确保单独成段且无连续空行）
            return re.sub(r'\n{3,}', '\n\n', new_block) + trailing_newline

        return block_pattern.sub(_replace_block, text)

    def _sanitize_special_chars(self, text: str) -> str:
        """转义 Markdown 特殊字符冲突（如 *_| 等）"""
        # 处理竖线替换为\vert
        text = re.sub(r'\|', r'\\vert ', text)
        
        # 处理未加括号的上下标（需要分两次匹配确保优先级）
        patterns = [
            # 处理带转义字符的情况（如 \alpha）
            (r'(_|\^)(\\[a-zA-Z]+)\b', r'\1{\2}'),
            # 处理单个字符的情况（非空格非花括号）
            (r'([_^])([^{}\s\\])', r'\1{\2}')
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        # 合并连续空格（保留单个空格）
        text = re.sub(r' {2,}', ' ', text)
        
        return text

    @staticmethod
    def _merge_consecutive_empty_lines(text: str) -> str:
        """合并连续同类空行，智能保持多重引用层级"""
        result = []
        # 状态追踪：前一行是否为同类空行及其层级
        prev_is_empty = {'type': None, 'level': 0}  # 'type': 'normal'/'block', 'level'为引用深度

        for line in text.split('\n'):
            stripped = line.strip()
            
            # 状态判断（时间复杂度O(1)）
            current_type = 'text'
            current_level = 0
            if not stripped:  # 普通空行
                current_type = 'normal'
            elif stripped.startswith('>'):
                # 精准层级计算（忽略内部空格）
                clean_line = stripped.replace(' ', '')
                if all(c == '>' for c in clean_line):  # 纯引用空行
                    current_type = 'block'
                    current_level = len(clean_line)
            
            # 合并决策逻辑
            if current_type == 'text':
                result.append(line)
                prev_is_empty = {'type': None, 'level': 0}
            else:
                # 同类同级空行合并
                if (prev_is_empty['type'] == current_type and 
                    prev_is_empty['level'] == current_level):
                    continue
                result.append(line)
                prev_is_empty = {'type': current_type, 'level': current_level}

        # 重建文本并处理跨行合并
        processed = '\n'.join(result)
        # 最终合并可能残留的连续空行（不影响层级）
        return re.sub(r'(\n{3,})', '\n\n', processed)

# 测试用代码
if __name__ == '__main__':
    c = MathJax_Converter()
    text = r'''$x^{a_{b}}$'''
    s = c.convert(text)
    print(s)
