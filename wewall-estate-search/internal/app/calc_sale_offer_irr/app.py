from internal import model, interface


async def CalcSaleOfferIRR(
        sale_offer_repo: interface.ISaleOfferRepo,
        sale_offer_service: interface.ISaleOfferService
):
    print("Start CalcSaleOfferIRR")
    sale_offers = await sale_offer_repo.all_sale_offer()

    for sale_offer in sale_offers:
        print(f"{sale_offer.id=}")
        await sale_offer_service.calc_sale_offer_irr(sale_offer)