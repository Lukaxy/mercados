"""Seeds the database with the original Bentão Atacado landing page content
so the site is fully functional immediately after a fresh install, without
requiring the admin to fill in every field manually first.

Run with: flask seed-db
"""

from datetime import date, timedelta

from app.extensions import db
from app.models import SiteSettings, HeroSlide, GalleryItem, Department, Offer


def run_seed():
    settings = SiteSettings.get_solo()
    settings.site_name = "Bentão Atacado"
    settings.site_tagline = "Sidrolândia - MS"
    settings.logo_text = "BENTÃO"
    settings.meta_description = (
        "O maior atacarejo de Sidrolândia - MS. Preços baixos em alimentos, "
        "hortifrúti e carnes."
    )
    settings.topbar_enabled = True
    settings.topbar_badge_text = "AO VIVO"
    settings.topbar_message = (
        "OFERTAS IMPERDÍVEIS DA SEMANA EM SIDROLÂNDIA - O MENOR PREÇO DO ATACADO!"
    )
    settings.whatsapp_number = "5567999999999"
    settings.whatsapp_default_message = "Olá! Vim pelo site e quero receber as ofertas!"
    settings.whatsapp_offer_message = "Quero o encarte da semana!"
    settings.hero_badge_text = "O Maior Atacarejo de Sidrolândia"
    settings.hero_title_line = "Economize de verdade no"
    settings.hero_title_highlight = "Varejo ou Atacado!"
    settings.hero_subtitle = (
        "No Bentão Atacado você garante preço baixo de verdade em alimentos, "
        "bebidas, hortifrúti fresco e carnes selecionadas. Tudo para o seu lar ou comércio!"
    )
    settings.hero_cta_primary_text = "VER ENCARTE DA SEMANA"
    settings.hero_cta_secondary_text = "COMO CHEGAR (MAPS)"
    settings.stat1_value, settings.stat1_label = "100%", "Preço Baixo"
    settings.stat2_value, settings.stat2_label = "+5.000", "Itens em Estoque"
    settings.stat3_value, settings.stat3_label = "7 Dias", "Aberto na Semana"
    settings.address_text = "Sidrolândia - MS"
    settings.hours_text = "Seg a Sáb: 07h às 20h | Dom: 07h às 12h"
    settings.maps_link = "https://maps.app.goo.gl/Hvurh7LC2RfngyPT8"
    settings.maps_embed_url = (
        "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3733.684128084055"
        "!2d-54.962134!3d-20.932822!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2"
        "!1s0x0%3A0x0!2zMjDCsDU1JzfeLjIiUyA1NMK0NTcnNDMuNyJX!5e0!3m2!1spt-BR!2sbr"
        "!4v1650000000000!5m2!1spt-BR!2sbr"
    )
    db.session.commit()

    if HeroSlide.query.count() == 0:
        slides = [
            (
                "https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=800&q=80",
                "Corredores Bentão",
            ),
            (
                "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=800&q=80",
                "Hortifrúti",
            ),
            (
                "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=800&q=80",
                "Açougue",
            ),
        ]
        for order, (url, alt) in enumerate(slides):
            db.session.add(
                HeroSlide(image_path=url, alt_text=alt, display_order=order, is_active=True)
            )

    if GalleryItem.query.count() == 0:
        items = [
            (
                "https://images.unsplash.com/photo-1578916171728-46686eac8d58?auto=format&fit=crop&w=800&q=80",
                "Atacado & Varejo",
                "Prateleiras Abastecidas",
                "yellow",
            ),
            (
                "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=800&q=80",
                "Frescor Diário",
                "Hortifrúti Selecionado",
                "emerald",
            ),
            (
                "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=800&q=80",
                "Qualidade Garantida",
                "Açougue Completo",
                "red",
            ),
        ]
        for order, (url, cat, title, color) in enumerate(items):
            db.session.add(
                GalleryItem(
                    image_path=url,
                    category_label=cat,
                    title=title,
                    color_theme=color,
                    display_order=order,
                    is_active=True,
                )
            )

    if Department.query.count() == 0:
        deps = [
            (
                "Mercearia",
                "mercearia",
                "fa-solid fa-basket-shopping",
                "Alimentos Básicos & Cesta Básica",
                "Arroz, feijão, óleo e enlatados com descontos especiais em fardos.",
            ),
            (
                "Hortifrúti",
                "hortifruti",
                "fa-solid fa-apple-whole",
                "Frutas, Verduras e Legumes",
                "Produtos selecionados diariamente com frescor garantido.",
            ),
            (
                "Açougue",
                "acougue",
                "fa-solid fa-drumstick-bite",
                "Açougue & Cortes Especiais",
                "Carnes nobres para o seu churrasco e refeições do dia a dia.",
            ),
        ]
        for order, (name, slug, icon, title, desc) in enumerate(deps):
            db.session.add(
                Department(
                    name=name,
                    slug=slug,
                    icon_class=icon,
                    title=title,
                    description=desc,
                    display_order=order,
                    is_active=True,
                )
            )

    if Offer.query.count() == 0:
        sample_offers = [
            ("Arroz Tipo 1 - Fardo 30kg", 89.90, 109.90, "fardo", "Mercearia", True),
            ("Óleo de Soja 900ml - Caixa c/20", 74.90, 89.90, "cx", "Mercearia", False),
            ("Picanha Bovina Resfriada", 39.90, 49.90, "kg", "Açougue", True),
            ("Melancia Selecionada", 2.49, 3.49, "kg", "Hortifrúti", False),
        ]
        for order, (name, price, old_price, unit, cat, highlight) in enumerate(sample_offers):
            db.session.add(
                Offer(
                    name=name,
                    price=price,
                    old_price=old_price,
                    unit=unit,
                    category=cat,
                    is_highlight=highlight,
                    is_active=True,
                    valid_until=date.today() + timedelta(days=7),
                    display_order=order,
                )
            )

    db.session.commit()
