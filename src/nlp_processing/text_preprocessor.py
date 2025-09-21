# -*- coding: utf-8 -*-
"""
文本预处理器
提供分词、词性标注、去停用词等文本预处理功能
"""

import re
from typing import List, Dict, Set, Optional, Tuple
import logging

try:
    import jieba
    import jieba.posseg as pseg
except ImportError:
    jieba = None
    pseg = None

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, WordNetLemmatizer
except ImportError:
    nltk = None
    stopwords = None
    word_tokenize = None
    sent_tokenize = None
    PorterStemmer = None
    WordNetLemmatizer = None

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    文本预处理器类
    提供中英文文本的预处理功能
    """
    
    def __init__(self, language: str = 'chinese'):
        """
        初始化文本预处理器
        
        Args:
            language: 语言类型，支持 'chinese', 'english'
        """
        self.language = language
        self.chinese_stopwords = self._load_chinese_stopwords()
        self.english_stopwords = self._load_english_stopwords()
        
        # 初始化词干提取器和词形还原器
        if PorterStemmer:
            self.stemmer = PorterStemmer()
        else:
            self.stemmer = None
            
        if WordNetLemmatizer:
            self.lemmatizer = WordNetLemmatizer()
        else:
            self.lemmatizer = None
    
    def _load_chinese_stopwords(self) -> Set[str]:
        """
        加载中文停用词表
        
        Returns:
            中文停用词集合
        """
        # 基础中文停用词
        basic_stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '里', '就是', '还是', '把', '比', '或者', '因为', '所以',
            '但是', '如果', '虽然', '然后', '而且', '不过', '只是', '可以', '应该', '能够',
            '已经', '正在', '将要', '可能', '必须', '需要', '希望', '想要', '喜欢', '觉得',
            '认为', '知道', '明白', '理解', '相信', '同意', '支持', '反对', '赞成'
        }
        
        return basic_stopwords
    
    def _load_english_stopwords(self) -> Set[str]:
        """
        加载英文停用词表
        
        Returns:
            英文停用词集合
        """
        if stopwords:
            try:
                return set(stopwords.words('english'))
            except:
                logger.warning("无法加载NLTK英文停用词，使用基础停用词")
        
        # 基础英文停用词
        basic_stopwords = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
            'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
            'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
            'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
            'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
            'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
            'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above',
            'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once'
        }
        
        return basic_stopwords
    
    def clean_text(self, text: str) -> str:
        """
        清理文本，去除特殊字符和多余空白
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 去除邮箱地址
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # 统一空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 去除首尾空白
        text = text.strip()
        
        return text
    
    def tokenize_chinese(self, text: str) -> List[str]:
        """
        中文分词
        
        Args:
            text: 中文文本
            
        Returns:
            分词结果列表
        """
        if not jieba:
            logger.warning("jieba未安装，使用简单字符分割")
            return list(text.replace(' ', ''))
        
        try:
            tokens = list(jieba.cut(text))
            # 过滤空白和单字符（除了有意义的单字）
            meaningful_single_chars = {'人', '事', '物', '地', '时', '钱', '车', '房', '书', '学', '工', '商'}
            filtered_tokens = []
            for token in tokens:
                token = token.strip()
                if len(token) > 1 or token in meaningful_single_chars:
                    filtered_tokens.append(token)
            return filtered_tokens
        except Exception as e:
            logger.error(f"中文分词失败: {str(e)}")
            return [text]
    
    def tokenize(self, text: str) -> List[str]:
        """分词 - 别名方法"""
        return self.word_tokenize(text)
    
    def word_tokenize(self, text: str) -> List[str]:
        """通用分词方法"""
        if self.language == 'chinese':
            return self.tokenize_chinese(text)
        else:
            return self.tokenize_english(text)
    
    def tokenize_english(self, text: str) -> List[str]:
        """
        英文分词
        
        Args:
            text: 英文文本
            
        Returns:
            分词结果列表
        """
        if word_tokenize:
            try:
                return word_tokenize(text.lower())
            except:
                logger.warning("NLTK分词失败，使用简单分割")
        
        # 简单的英文分词
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    def pos_tag_chinese(self, text: str) -> List[Tuple[str, str]]:
        """
        中文词性标注
        
        Args:
            text: 中文文本
            
        Returns:
            (词, 词性) 元组列表
        """
        if not pseg:
            logger.warning("jieba.posseg未安装，无法进行词性标注")
            tokens = self.tokenize_chinese(text)
            return [(token, 'unknown') for token in tokens]
        
        try:
            words = pseg.cut(text)
            return [(word, flag) for word, flag in words if word.strip()]
        except Exception as e:
            logger.error(f"中文词性标注失败: {str(e)}")
            tokens = self.tokenize_chinese(text)
            return [(token, 'unknown') for token in tokens]
    
    def remove_stopwords(self, tokens: List[str], language: str = None) -> List[str]:
        """
        去除停用词
        
        Args:
            tokens: 词汇列表
            language: 语言类型，默认使用初始化时的语言
            
        Returns:
            去除停用词后的词汇列表
        """
        if language is None:
            language = self.language
        
        if language == 'chinese':
            stopwords_set = self.chinese_stopwords
        elif language == 'english':
            stopwords_set = self.english_stopwords
        else:
            stopwords_set = set()
        
        return [token for token in tokens if token not in stopwords_set]
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        提取句子
        
        Args:
            text: 文本
            
        Returns:
            句子列表
        """
        if self.language == 'chinese':
            # 中文句子分割
            sentences = re.split(r'[。！？；\n]+', text)
        else:
            # 英文句子分割
            if sent_tokenize:
                try:
                    sentences = sent_tokenize(text)
                except:
                    sentences = re.split(r'[.!?\n]+', text)
            else:
                sentences = re.split(r'[.!?\n]+', text)
        
        # 过滤空句子
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def stem_words(self, tokens: List[str]) -> List[str]:
        """
        词干提取（仅适用于英文）
        
        Args:
            tokens: 词汇列表
            
        Returns:
            词干提取后的词汇列表
        """
        if not self.stemmer:
            logger.warning("词干提取器未初始化")
            return tokens
        
        try:
            return [self.stemmer.stem(token) for token in tokens]
        except Exception as e:
            logger.error(f"词干提取失败: {str(e)}")
            return tokens
    
    def lemmatize_words(self, tokens: List[str]) -> List[str]:
        """
        词形还原（仅适用于英文）
        
        Args:
            tokens: 词汇列表
            
        Returns:
            词形还原后的词汇列表
        """
        if not self.lemmatizer:
            logger.warning("词形还原器未初始化")
            return tokens
        
        try:
            return [self.lemmatizer.lemmatize(token) for token in tokens]
        except Exception as e:
            logger.error(f"词形还原失败: {str(e)}")
            return tokens
    
    def preprocess_text(self, text: str, 
                       remove_stopwords: bool = True,
                       extract_pos: bool = False) -> Dict[str, any]:
        """
        完整的文本预处理流程
        
        Args:
            text: 原始文本
            remove_stopwords: 是否去除停用词
            extract_pos: 是否提取词性
            
        Returns:
            预处理结果字典
        """
        result = {
            'original_text': text,
            'cleaned_text': '',
            'sentences': [],
            'tokens': [],
            'pos_tags': [],
            'filtered_tokens': []
        }
        
        if not text:
            return result
        
        # 1. 清理文本
        cleaned_text = self.clean_text(text)
        result['cleaned_text'] = cleaned_text
        
        # 2. 提取句子
        sentences = self.extract_sentences(cleaned_text)
        result['sentences'] = sentences
        
        # 3. 分词
        if self.language == 'chinese':
            tokens = self.tokenize_chinese(cleaned_text)
        else:
            tokens = self.tokenize_english(cleaned_text)
        result['tokens'] = tokens
        
        # 4. 词性标注
        if extract_pos and self.language == 'chinese':
            pos_tags = self.pos_tag_chinese(cleaned_text)
            result['pos_tags'] = pos_tags
        
        # 5. 去除停用词
        if remove_stopwords:
            filtered_tokens = self.remove_stopwords(tokens)
        else:
            filtered_tokens = tokens
        
        # 6. 英文词干提取/词形还原
        if self.language == 'english':
            if self.stemmer:
                filtered_tokens = self.stem_words(filtered_tokens)
            elif self.lemmatizer:
                filtered_tokens = self.lemmatize_words(filtered_tokens)
        
        result['filtered_tokens'] = filtered_tokens
        
        return result
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        提取关键词（基于词频）
        
        Args:
            text: 文本
            top_k: 返回前k个关键词
            
        Returns:
            (关键词, 权重) 元组列表
        """
        preprocessed = self.preprocess_text(text, remove_stopwords=True)
        tokens = preprocessed['filtered_tokens']
        
        if not tokens:
            return []
        
        # 计算词频
        word_freq = {}
        for token in tokens:
            if len(token) > 1:  # 过滤单字符
                word_freq[token] = word_freq.get(token, 0) + 1
        
        # 计算TF权重
        total_words = len(tokens)
        tf_scores = {word: freq / total_words for word, freq in word_freq.items()}
        
        # 按权重排序
        sorted_keywords = sorted(tf_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords[:top_k]
    
    def get_text_statistics(self, text: str) -> Dict[str, int]:
        """
        获取文本统计信息
        
        Args:
            text: 文本
            
        Returns:
            统计信息字典
        """
        preprocessed = self.preprocess_text(text)
        
        return {
            'char_count': len(text),
            'word_count': len(preprocessed['tokens']),
            'sentence_count': len(preprocessed['sentences']),
            'unique_words': len(set(preprocessed['tokens'])),
            'avg_sentence_length': len(preprocessed['tokens']) / max(len(preprocessed['sentences']), 1)
        }