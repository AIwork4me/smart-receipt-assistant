"""LangChain 兼容层

解决 paddlex 包与新版 LangChain 的兼容性问题。
paddlex 使用了旧版 LangChain 的导入路径，这些路径在新版中已被移除。

此模块必须在导入 langchain_paddleocr 之前被导入。
"""
import sys
from types import ModuleType


def setup_langchain_compat():
    """设置 LangChain 兼容层

    为旧版 LangChain 导入路径创建兼容模块：
    - langchain.docstore.document -> langchain_core.documents
    - langchain.text_splitter -> langchain_text_splitters

    注意：不会覆盖真实的 langchain 包，只是添加缺失的子模块。
    """
    # 首先确保真实的 langchain 包被导入
    try:
        import langchain
        # langchain 包已存在，不需要创建假的模块
    except ImportError:
        # 如果 langchain 包不存在，才创建假的模块
        if 'langchain' not in sys.modules:
            langchain_module = ModuleType('langchain')
            sys.modules['langchain'] = langchain_module

    # 导入新版模块
    import langchain_core.documents
    import langchain_text_splitters

    # 创建 langchain.docstore 兼容模块
    if 'langchain.docstore' not in sys.modules:
        docstore_module = ModuleType('langchain.docstore')
        sys.modules['langchain.docstore'] = docstore_module

    # 创建 langchain.docstore.document 兼容模块
    if 'langchain.docstore.document' not in sys.modules:
        document_module = ModuleType('langchain.docstore.document')
        document_module.Document = langchain_core.documents.Document
        sys.modules['langchain.docstore.document'] = document_module

    # 创建 langchain.text_splitter 兼容模块
    if 'langchain.text_splitter' not in sys.modules:
        text_splitter_module = ModuleType('langchain.text_splitter')
        # 复制所有公共属性
        for attr in dir(langchain_text_splitters):
            if not attr.startswith('_'):
                setattr(text_splitter_module, attr, getattr(langchain_text_splitters, attr))
        sys.modules['langchain.text_splitter'] = text_splitter_module


# 自动设置兼容层
setup_langchain_compat()
