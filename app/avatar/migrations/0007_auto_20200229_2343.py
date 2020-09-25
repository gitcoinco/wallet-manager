# Generated by Django 2.2.4 on 2020-02-29 23:43

from django.db import migrations
from django.templatetags.static import static


def get_preview_img(key):
    if key == "classic":
        return (
            "https://c.gitcoin.co/avatars/d1a33d2bcb7bbfef50368bca73111fae/fryggr.png"
        )
    if key == "bufficorn":
        return (
            "https://c.gitcoin.co/avatars/94c30306a088d06163582da942a2e64e/dah0ld3r.png"
        )
    if key == "female":
        return "https://c.gitcoin.co/avatars/b713fb593b3801700fd1f92e9cd18e79/aaliyahansari.png"
    if key == "unisex":
        return "https://c.gitcoin.co/avatars/cc8272136bcf9b9d830c0554a97082f3/joshegwuatu.png"
    if key == "bot":
        return (
            "https://c.gitcoin.co/avatars/c9d82da31b7833bdae37861014c32ebc/owocki.png"
        )
    return static(f"v2/images/avatar3d/{key}.png")


def get_artist_bio(key):
    if key == "metacartel":
        return 'This piece was originally created by <a target="_blank" href="https://twitter.com/frankynines">@frankynies</a>, an amazing artist of Mexican heritage who works at Dapper Labs.'
    if key == "comic":
        return 'This piece was created by <a target=new href="/TheDataDesigner">@TheDataDesigner</a>.'
    if key == "square_bot":
        return (
            'This piece was created by <a target=new href="/octaviaan">@octaviaan</a>.'
        )
    if key == "cartoon_jedi":
        return (
            'This piece was created by <a target=new href="/Popeline5">@Popeline5</a>.'
        )
    if key == "jedi" or key == "orc" or key == "joker":
        return 'This piece was created by <a target=new href="/KushMd">@KushMd </a>.'
    if key == "unisex" or key == "female":
        return 'This piece was created by <a target=new href="/MladenPetronijevic">@MladenPetronijevic</a>.'
    if key == "bot":
        return 'This piece was created by <a target=new href="/GuistF">@GuistF</a>.'
    if key == "bufficorn":
        return 'The Bufficorn was created by <a target="_blank" href="https://twitter.com/EthereumDenver">@EthereumDenver</a>.'
    return ""


def get_avatar_info(key):
    if key == "classic":
        return "The classic avatar builder.  Built by & for Gitcoiners with bounties."
    if key == "unisex" or key == "female":
        return "A fun new avatar style that hit the streets in 2019"
    if key == "bufficorn":
        return "The Bufficorn is a magical fantastical animal that represents the collaborative spirit of #BUIDL. They live in communities atop Colorados 14er mountain peaks and strive to serve their communities above their own selfish interests. "
    if key == "bot":
        return "Bots are a Gitcoin favorite.  Beep Boop bop"
    if key in ["flat", "shiny", "people", "technology", "landscape", "space"]:
        return 'Liscensed under Creative Commons from our friends at <a target=new href="https://svgrepo.com">svgrepo.com</a>'
    return ""


def get_avatar_options():
    avatar_options = [
        "classic",
        "unisex",
        "female",
        "bufficorn",
        "square_bot",
        "bot",
        "comic",
        "flat",
        "shiny",
        "people",
        "robot",
        "technology",
        "landscape",
        "space",
        "spring",
        "metacartel",
        "jedi",
        "orc",
        "joker",
        "cartoon_jedi",
    ]
    avatar_options = [
        (
            ele,
            f"/onboard/profile?steps=avatar&theme={ele}",
            get_preview_img(ele),
            get_artist_bio(ele),
            get_avatar_info(ele),
        )
        for ele in avatar_options
    ]
    return avatar_options


def forwards(apps, schema_editor):
    AvatarTheme = apps.get_model("avatar", "AvatarTheme")
    for ele in get_avatar_options():
        AvatarTheme.objects.create(
            active=True,
            description=ele[4],
            artist_bio=ele[3],
            name=ele[0],
            popularity=0,
            tags=[],
            img_url=ele[2],
        )


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("avatar", "0006_avatartheme"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
