from internal import model, interface


async def M2DataParsing(
        db: interface.IDB,
        estate_service: interface.IEstateService,
        rent_offer_service: interface.IRentOfferService,
        sale_offer_service: interface.ISaleOfferService,
        m2data_parser: interface.IM2DataParser,
):
    # await db.multi_query(model.create_queries)

    estates = m2data_parser.parse()
    print(f"{estates}", flush=True)
    for estate in estates:
        estate_id = await estate_service.create_estate(
            estate.link,
            estate.name,
            estate.category,
            estate.address,
            estate.coords,
            estate.metro_stations,
        )
        print(f"{estate_id}", flush=True)

        for rent_offer in estate.rent_offers:
            rent_offer_id = await rent_offer_service.create_rent_offer(
                estate_id,
                rent_offer.link,
                rent_offer.name,
                rent_offer.square,
                rent_offer.price_per_month,
                rent_offer.design,
                rent_offer.floor,
                rent_offer.type,
                rent_offer.location,
                rent_offer.image_urls,
                rent_offer.offer_readiness,
                rent_offer.readiness_date,
                rent_offer.description
            )
            print(f"{rent_offer_id}", flush=True)

        for sale_offer in estate.sale_offers:
            sale_offer_id = await sale_offer_service.create_sale_offer(
                estate_id,
                sale_offer.link,
                sale_offer.name,
                sale_offer.square,
                sale_offer.price,
                sale_offer.price_per_meter,
                sale_offer.design,
                sale_offer.floor,
                sale_offer.type,
                sale_offer.location,
                sale_offer.image_urls,
                sale_offer.offer_readiness,
                sale_offer.readiness_date,
                sale_offer.description,
            )
            print(f"{sale_offer_id}", flush=True)


async def TrendAgentParsing(
        estate_service: interface.IEstateService,
        sale_offer_service: interface.ISaleOfferService,
        trend_agent_parser: interface.ITrendAgentParser,
):
    print("Start TrendAgentParsing", flush=True)
    estates = trend_agent_parser.parse()
    # print(f"{estates=}")
    for estate in estates:
        estate_id = await estate_service.create_estate(
            estate.link,
            estate.name,
            estate.category,
            estate.address,
            estate.coords,
            estate.metro_stations,
        )
        print(f"{estate_id=}", flush=True)

        for sale_offer in estate.sale_offers:
            sale_offer_id = await sale_offer_service.create_sale_offer(
                estate_id,
                sale_offer.link,
                sale_offer.name,
                sale_offer.square,
                sale_offer.price,
                sale_offer.price_per_meter,
                sale_offer.design,
                sale_offer.floor,
                sale_offer.type,
                sale_offer.location,
                sale_offer.image_urls,
                sale_offer.offer_readiness,
                sale_offer.readiness_date,
                sale_offer.description
            )
            print(f"{sale_offer_id=}", flush=True)