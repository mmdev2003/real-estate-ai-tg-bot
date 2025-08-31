import json
from opentelemetry.trace import SpanKind, Status, StatusCode

from internal import interface, model
from .query import *


class EstateSearchStateRepo(interface.IEstateSearchStateRepo):
    def __init__(self, tel: interface.ITelemetry, db: interface.IDB):
        self.db = db
        self.tracer = tel.tracer()

    async def create_estate_search_state(
            self,
            state_id: int,
            offers: list[model.SaleOffer | model.RentOffer],
            estate_search_params: dict
    ) -> int:
        with self.tracer.start_as_current_span(
                "EstateSearchStateRepo.create_estate_search_state",
                kind=SpanKind.INTERNAL,
                attributes={
                    "state_id": state_id,
                    "offers": str(offers),
                    "estate_search_params": str(estate_search_params)
                }
        ) as span:
            try:
                args = {
                    "state_id": state_id,
                    "offers": [json.dumps(offer.to_dict(), ensure_ascii=False) for offer in offers],
                    "estate_search_params": json.dumps(estate_search_params, ensure_ascii=False)
                }
                offer_id = await self.db.insert(create_estate_search_state_query, args)

                span.set_status(StatusCode.OK)
                return offer_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def change_current_offer_by_state_id(self, state_id: int, current_offer_id: int) -> None:
        with self.tracer.start_as_current_span(
                "EstateSearchStateRepo.change_current_offer_by_state_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "state_id": state_id,
                    "current_offer_id": current_offer_id
                }
        ) as span:
            try:
                args = {"state_id": state_id, "current_offer_id": current_offer_id}
                await self.db.update(change_current_offer_by_state_id_query, args)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def change_current_estate_by_state_id(self, state_id: int, current_estate_id: int) -> None:
        with self.tracer.start_as_current_span(
                "EstateSearchStateRepo.change_current_estate_by_state_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "state_id": state_id,
                    "current_estate_id": current_estate_id
                }
        ) as span:
            try:
                args = {"state_id": state_id, "current_estate_id": current_estate_id}
                await self.db.update(change_current_estate_by_state_id_query, args)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def estate_search_state_by_state_id(self, state_id: int) -> list[model.EstateSearchState]:
        with self.tracer.start_as_current_span(
                "EstateSearchStateRepo.estate_search_state_by_state_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "state_id": state_id,
                }
        ) as span:
            try:
                args = {"state_id": state_id}
                rows = await self.db.select(estate_search_state_by_state_id_query, args)
                if rows:
                    rows = model.EstateSearchState.serialize(rows)

                span.set_status(StatusCode.OK)
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err


    async def delete_estate_search_state_by_state_id(self, state_id: int) -> None:
        with self.tracer.start_as_current_span(
                "EstateSearchStateRepo.delete_estate_search_state_by_state_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "state_id": state_id,
                }
        ) as span:
            try:
                args = {"state_id": state_id}
                await self.db.delete(delete_estate_search_state_by_state_id_query, args)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
