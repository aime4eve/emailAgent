# -*- coding: utf-8 -*-
"""
文本处理工具模块

提供文本预处理、清洗、分词等功能。
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import unicodedata

@dataclass
class TextProcessingResult:
    """文本处理结果数据类"""
    original_text: str
    processed_text: str
    tokens: List[str]
    sentences: List[str]
    metadata: Dict[str, Any]
    
class TextProcessor:
    """文本处理器类
    
    提供文本预处理、清洗、分词等功能。
    """
    
    def __init__(self):
        """初始化文本处理器"""
        self.logger = logging.getLogger(__name__)
        
        # 停用词列表（简化版）
        self.stop_words = {
            'zh': ['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'],
            'en': ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should']
        }
        
        # 标点符号
        self.punctuation = '！？。，；：""''（）【】《》.,;:!?()[]{}'
        
        # 数字和字母的正则表达式
        self.number_pattern = re.compile(r'\d+(?:\.\d+)?')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
    def clean_text(self, text: str, remove_punctuation: bool = False, 
                   remove_numbers: bool = False, remove_emails: bool = False,
                   remove_urls: bool = False, normalize_whitespace: bool = True) -> str:
        """清洗文本
        
        Args:
            text: 原始文本
            remove_punctuation: 是否移除标点符号
            remove_numbers: 是否移除数字
            remove_emails: 是否移除邮箱地址
            remove_urls: 是否移除URL
            normalize_whitespace: 是否规范化空白字符
            
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
            
        try:
            # 移除URL
            if remove_urls:
                text = self.url_pattern.sub('', text)
                
            # 移除邮箱
            if remove_emails:
                text = self.email_pattern.sub('', text)
                
            # 移除数字
            if remove_numbers:
                text = self.number_pattern.sub('', text)
                
            # 移除标点符号
            if remove_punctuation:
                text = ''.join(char for char in text if char not in self.punctuation)
                
            # 规范化空白字符
            if normalize_whitespace:
                text = re.sub(r'\s+', ' ', text).strip()
                
            # Unicode规范化
            text = unicodedata.normalize('NFKC', text)
            
            return text
            
        except Exception as e:
            self.logger.error(f"文本清洗失败: {e}")
            return text
            
    def tokenize(self, text: str, language: str = 'auto') -> List[str]:
        """文本分词
        
        Args:
            text: 输入文本
            language: 语言类型 ('zh', 'en', 'auto')
            
        Returns:
            分词结果列表
        """
        if not text:
            return []
            
        try:
            # 自动检测语言
            if language == 'auto':
                language = self.detect_language(text)
                
            # 中文分词（简化版）
            if language == 'zh':
                tokens = self._tokenize_chinese(text)
            else:
                tokens = self._tokenize_english(text)
                
            # 过滤空白和短词
            tokens = [token.strip() for token in tokens if token.strip() and len(token.strip()) > 1]
            
            return tokens
            
        except Exception as e:
            self.logger.error(f"分词失败: {e}")
            return text.split()
            
    def _tokenize_chinese(self, text: str) -> List[str]:
        """中文分词（简化版）
        
        Args:
            text: 中文文本
            
        Returns:
            分词结果
        """
        # 简化的中文分词，实际应该使用jieba等专业分词工具
        tokens = []
        
        # 按标点符号分割
        segments = re.split(r'[，。！？；：、\s]+', text)
        
        for segment in segments:
            if segment.strip():
                # 简单的字符级分割（实际应该使用词典匹配）
                words = []
                current_word = ""
                
                for char in segment:
                    if self._is_chinese_char(char):
                        if len(current_word) >= 2:  # 假设词长度为2-4
                            words.append(current_word)
                            current_word = char
                        else:
                            current_word += char
                    else:
                        if current_word:
                            words.append(current_word)
                            current_word = ""
                        if char.strip():
                            words.append(char)
                            
                if current_word:
                    words.append(current_word)
                    
                tokens.extend(words)
                
        return tokens
        
    def _tokenize_english(self, text: str) -> List[str]:
        """英文分词
        
        Args:
            text: 英文文本
            
        Returns:
            分词结果
        """
        # 英文按空格和标点分词
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
        
    def _is_chinese_char(self, char: str) -> bool:
        """判断是否为中文字符
        
        Args:
            char: 字符
            
        Returns:
            是否为中文字符
        """
        return '\u4e00' <= char <= '\u9fff'
        
    def detect_language(self, text: str) -> str:
        """检测文本语言
        
        Args:
            text: 输入文本
            
        Returns:
            语言代码 ('zh', 'en')
        """
        if not text:
            return 'en'
            
        # 统计中文字符比例
        chinese_chars = sum(1 for char in text if self._is_chinese_char(char))
        total_chars = len([char for char in text if char.isalnum()])
        
        if total_chars == 0:
            return 'en'
            
        chinese_ratio = chinese_chars / total_chars
        
        return 'zh' if chinese_ratio > 0.3 else 'en'
        
    def remove_stop_words(self, tokens: List[str], language: str = 'auto') -> List[str]:
        """移除停用词
        
        Args:
            tokens: 词汇列表
            language: 语言类型
            
        Returns:
            过滤后的词汇列表
        """
        if not tokens:
            return []
            
        try:
            if language == 'auto':
                # 基于词汇内容判断语言
                text_sample = ' '.join(tokens[:10])
                language = self.detect_language(text_sample)
                
            stop_words = self.stop_words.get(language, [])
            filtered_tokens = [token for token in tokens if token.lower() not in stop_words]
            
            return filtered_tokens
            
        except Exception as e:
            self.logger.error(f"停用词过滤失败: {e}")
            return tokens
            
    def extract_sentences(self, text: str, language: str = 'auto') -> List[str]:
        """提取句子
        
        Args:
            text: 输入文本
            language: 语言类型
            
        Returns:
            句子列表
        """
        if not text:
            return []
            
        try:
            if language == 'auto':
                language = self.detect_language(text)
                
            if language == 'zh':
                # 中文句子分割
                sentences = re.split(r'[。！？；]', text)
            else:
                # 英文句子分割
                sentences = re.split(r'[.!?;]', text)
                
            # 清理和过滤句子
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]
            
            return sentences
            
        except Exception as e:
            self.logger.error(f"句子提取失败: {e}")
            return [text]
            
    def extract_keywords(self, text: str, top_k: int = 10, min_length: int = 2) -> List[Tuple[str, float]]:
        """提取关键词
        
        Args:
            text: 输入文本
            top_k: 返回前k个关键词
            min_length: 最小词长度
            
        Returns:
            关键词及其权重的列表
        """
        if not text:
            return []
            
        try:
            # 文本预处理
            cleaned_text = self.clean_text(text, remove_punctuation=True)
            tokens = self.tokenize(cleaned_text)
            tokens = self.remove_stop_words(tokens)
            
            # 过滤短词
            tokens = [token for token in tokens if len(token) >= min_length]
            
            # 计算词频
            word_freq = {}
            for token in tokens:
                word_freq[token] = word_freq.get(token, 0) + 1
                
            # 计算TF权重（简化版）
            total_words = len(tokens)
            keyword_scores = []
            
            for word, freq in word_freq.items():
                tf = freq / total_words
                # 简化的权重计算（实际应该使用TF-IDF）
                score = tf * (1 + len(word) / 10)  # 长词获得更高权重
                keyword_scores.append((word, score))
                
            # 按权重排序
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:top_k]
            
        except Exception as e:
            self.logger.error(f"关键词提取失败: {e}")
            return []
            
    def process_text(self, text: str, **kwargs) -> TextProcessingResult:
        """综合文本处理
        
        Args:
            text: 输入文本
            **kwargs: 处理参数
            
        Returns:
            文本处理结果
        """
        if not text:
            return TextProcessingResult(
                original_text="",
                processed_text="",
                tokens=[],
                sentences=[],
                metadata={}
            )
            
        try:
            # 检测语言
            language = self.detect_language(text)
            
            # 文本清洗
            processed_text = self.clean_text(
                text,
                remove_punctuation=kwargs.get('remove_punctuation', False),
                remove_numbers=kwargs.get('remove_numbers', False),
                remove_emails=kwargs.get('remove_emails', True),
                remove_urls=kwargs.get('remove_urls', True)
            )
            
            # 分词
            tokens = self.tokenize(processed_text, language)
            
            # 移除停用词
            if kwargs.get('remove_stop_words', True):
                tokens = self.remove_stop_words(tokens, language)
                
            # 提取句子
            sentences = self.extract_sentences(text, language)
            
            # 提取关键词
            keywords = self.extract_keywords(text, top_k=kwargs.get('top_keywords', 10))
            
            # 生成元数据
            metadata = {
                'language': language,
                'original_length': len(text),
                'processed_length': len(processed_text),
                'token_count': len(tokens),
                'sentence_count': len(sentences),
                'keywords': keywords,
                'processing_time': datetime.now().isoformat()
            }
            
            return TextProcessingResult(
                original_text=text,
                processed_text=processed_text,
                tokens=tokens,
                sentences=sentences,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"文本处理失败: {e}")
            return TextProcessingResult(
                original_text=text,
                processed_text=text,
                tokens=text.split(),
                sentences=[text],
                metadata={'error': str(e)}
            )
            
    def calculate_similarity(self, text1: str, text2: str, method: str = 'jaccard') -> float:
        """计算文本相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            method: 相似度计算方法 ('jaccard', 'cosine')
            
        Returns:
            相似度分数 (0-1)
        """
        if not text1 or not text2:
            return 0.0
            
        try:
            # 文本预处理
            tokens1 = set(self.tokenize(self.clean_text(text1, remove_punctuation=True)))
            tokens2 = set(self.tokenize(self.clean_text(text2, remove_punctuation=True)))
            
            if method == 'jaccard':
                # Jaccard相似度
                intersection = len(tokens1.intersection(tokens2))
                union = len(tokens1.union(tokens2))
                return intersection / union if union > 0 else 0.0
                
            elif method == 'cosine':
                # 简化的余弦相似度
                intersection = len(tokens1.intersection(tokens2))
                magnitude1 = len(tokens1) ** 0.5
                magnitude2 = len(tokens2) ** 0.5
                return intersection / (magnitude1 * magnitude2) if magnitude1 * magnitude2 > 0 else 0.0
                
            else:
                raise ValueError(f"不支持的相似度计算方法: {method}")
                
        except Exception as e:
            self.logger.error(f"相似度计算失败: {e}")
            return 0.0
            
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """获取文本统计信息
        
        Args:
            text: 输入文本
            
        Returns:
            统计信息字典
        """
        if not text:
            return {}
            
        try:
            # 基本统计
            char_count = len(text)
            word_count = len(text.split())
            sentence_count = len(self.extract_sentences(text))
            
            # 语言检测
            language = self.detect_language(text)
            
            # 分词统计
            tokens = self.tokenize(text)
            unique_tokens = len(set(tokens))
            
            # 词汇丰富度
            lexical_diversity = unique_tokens / len(tokens) if tokens else 0
            
            # 平均词长
            avg_word_length = sum(len(token) for token in tokens) / len(tokens) if tokens else 0
            
            # 平均句长
            sentences = self.extract_sentences(text)
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            
            return {
                'character_count': char_count,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'unique_word_count': unique_tokens,
                'language': language,
                'lexical_diversity': round(lexical_diversity, 3),
                'average_word_length': round(avg_word_length, 2),
                'average_sentence_length': round(avg_sentence_length, 2),
                'readability_score': self._calculate_readability_score(text)
            }
            
        except Exception as e:
            self.logger.error(f"文本统计失败: {e}")
            return {'error': str(e)}
            
    def _calculate_readability_score(self, text: str) -> float:
        """计算可读性分数（简化版）
        
        Args:
            text: 输入文本
            
        Returns:
            可读性分数 (0-100)
        """
        try:
            sentences = self.extract_sentences(text)
            words = text.split()
            
            if not sentences or not words:
                return 0.0
                
            # 平均句长
            avg_sentence_length = len(words) / len(sentences)
            
            # 平均词长
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # 简化的可读性公式
            readability = 100 - (avg_sentence_length * 1.5) - (avg_word_length * 2)
            
            return max(0, min(100, readability))
            
        except Exception as e:
            self.logger.error(f"可读性计算失败: {e}")
            return 50.0  # 默认中等可读性