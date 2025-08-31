from abc import abstractmethod
from typing import Protocol

from internal import model


class IAnalysisService(Protocol):
    @abstractmethod
    async def analysis_from_pdf(self, ctx: dict, pdf_path: str) -> int: pass


class IAnalysisRepo(Protocol):
    @abstractmethod
    async def all_analysis(self) -> list[model.Analysis]: pass

    @abstractmethod
    async def create_analysis(self, analysis_name: str, analysis_summary: str) -> int: pass
