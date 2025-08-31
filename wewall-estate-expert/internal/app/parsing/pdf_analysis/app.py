from pathlib import Path

from internal import interface


async def PdfAnalysisParsing(
        analysis_service: interface.IAnalysisService,
):
    ctx = {}
    for pdf_path in [f.name for f in Path("pkg/analysis_pdf").iterdir() if f.is_file()]:
        print(f"Analyzing pdf {pdf_path}\n\n", flush=True)
        await analysis_service.analysis_from_pdf(ctx, "pkg/analysis_pdf/" +pdf_path)
