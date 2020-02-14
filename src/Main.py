import pygame as pg
import json
from urllib.request import Request, urlopen
import ssl
import os
import Checkbox

#Run method is called by run class to start application
def run():
    pg.init()

    gameDisplay = pg.display.set_mode((800, 800))
    gameDisplay.fill([99, 99, 99])
    pg.display.set_caption('Stats Displayer')
    img = pg.image.load("logo.jpg")
    pg.display.set_icon(img)

    clock = pg.time.Clock()
    crashed = False

    font = pg.font.Font(None, 32)
    font2 = pg.font.Font(None, 82)
    color_inactive = (190, 190, 190)
    color_active = (219, 219, 219)
    color = color_inactive
    active = False
    text = ''
    done = False

    input_box = pg.Rect(200, 300, 400, 50)
    button_box = pg.Rect(350, 400, 100, 50)

    buttonClicked = False

    timer = 0

    dictionary = {}
    initial_draw = False

    while not crashed:
        gameDisplay.fill([99, 99, 99])
        for event in pg.event.get():
            if event.type == pg.QUIT:
                crashed = True

            if event.type == pg.QUIT:
                done = True
            if event.type == pg.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                elif button_box.collidepoint(event.pos):
                    buttonClicked = True
                    dictionary = returnStats(text)
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_RETURN:
                        print(text)
                        text = ''
                    elif event.key == pg.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        if buttonClicked == False:
            txt_surface = font.render(text, True, color)
            title_surface = font.render("Stats Displayer", True, color_inactive)
            predict_surface = font.render("Display", True, (96, 96, 96))
            width = max(400, txt_surface.get_width() + 10)
            input_box.w = width
            gameDisplay.blit(txt_surface, (input_box.x + 15, input_box.y + 15))
            gameDisplay.blit(title_surface, (315, 200))
            pg.draw.rect(gameDisplay, color, input_box, 2)
            pg.draw.rect(gameDisplay, color_inactive, button_box)
            gameDisplay.blit(predict_surface, (button_box.x + 11, button_box.y + 15))
        else:
            if text == '' or dictionary == {"rank":0, "wins":0, "losses":0, "ties":0, "max_score":0, "opr":0, "dpr":0} or dictionary == 0:
                error_surface = font.render("Please choose a valid team!!", True, color_inactive)
                gameDisplay.blit(error_surface, (250, 100))
                buttonClicked = False
            else:
                gameDisplay.fill([99, 99, 99])
                buttonClicked = render(gameDisplay, text, font, font2, color, timer, dictionary)
                timer += 0.1

        pg.display.update()
        clock.tick(60)

    pg.quit()
    quit()

#Render method updates window and does backend computation at a constant frame rate as well
def render(gamedisplay, text, font, font2, color, timer, dictionary):
    pg.draw.polygon(gamedisplay, (129, 129, 129), [(500, 200), (422, 238), (403, 322), (457, 390), (543, 390), (597, 322), (578, 238)], 2)
    pg.draw.polygon(gamedisplay, (129, 129, 129), [(500,100), (344,175), (305,345), (413,480), (587,480), (695,345), (656,175)], 2)

    stats = dictionary
    coords = [(475,78), (304,145), (205,350), (390,485), (550,485), (695,345), (656,148)]

    node_coords = [(500, 300 - (200*(57-stats["rank"])/57)), (500 - (156*(stats["wins"])/8), 300 - (125*(stats["wins"]/8))),
                       (500 - (195*(6-stats["losses"])/6), 300 + (45*(6-stats["losses"])/6)), (500-(87*stats["ccwm"]/16), 300 + (180*stats["ccwm"]/16)),
                       (500 + (87*stats["max_score"]/41), 300+(180*stats["max_score"]/41)), (500 + (195*stats["opr"]/22), 300+(45*stats["opr"]/22)),
                       (500 + (156*(12.4-stats["dpr"])/12.4), 300 - (125*(12.4-stats["dpr"])/12.4))]

    index = 0
    for i in stats:
        if i == "losses":
            i = "loss_eff"
        elif i == "dpr":
            i = "dpr_eff"
        surface = font.render(i, True, color)
        gamedisplay.blit(surface, coords[index])
        index += 1

    chance_surface = font.render("Chance of Winning", True, (190, 190, 190))
    chanceOfWinning = (((57-stats["rank"])/57)+((stats["wins"])/16)+(stats["opr"]/22))/3

    gamedisplay.blit(chance_surface, ((500+(chanceOfWinning*200))/2, 690))
    percent_surface = font.render(str(int(chanceOfWinning * 10000)/100)+"%", True, (190, 190, 190))
    gamedisplay.blit(percent_surface, ((200 + (chanceOfWinning * 400)) + 15, 640))

    team_name = font2.render(text, True, (190, 190, 190))
    gamedisplay.blit(team_name, (50, 200))

    predict_surface = font.render("Back", True, (96, 96, 96))
    button_box = pg.Rect(50, 50, 100, 50)
    pg.draw.rect(gamedisplay, (190, 190, 190), button_box)
    gamedisplay.blit(predict_surface, (button_box.x + 23, button_box.y + 15))
    pg.draw.rect(gamedisplay, (209, 226, 255), (200, 620, (400*chanceOfWinning), 50))

    pg.draw.polygon(gamedisplay, ((255 - (300 * chanceOfWinning)), 300 * chanceOfWinning, 0), node_coords)

    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            if button_box.collidepoint(event.pos):
                return False
    return True

#Main function calculates average of each of the stats and returns a dictionary with the computed output
def returnStats(teamName):
    url = "https://api.vexdb.io/v1/get_rankings?season=Tower%20Takeover&team=" + teamName
    req = Request(url, headers={'X-Mashape-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'})
    gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    info = urlopen(req, context=gcontext).read()
    teamsData = json.loads(info)

    rank = 0
    wins = 0
    losses = 0
    ccwm = 0
    max_score = 0
    opr = 0
    dpr = 0

    count = 0

    for i in teamsData["result"]:
        if i["team"] == teamName:
            rank += i["rank"]
            wins += i["wins"]
            losses += i["losses"]
            ccwm += i["ccwm"]
            max_score += i["max_score"]
            opr += i["opr"]
            dpr += i["dpr"]
            count += 1
    if count == 0:
        return 0
    return {"rank":rank/count, "wins":wins/count, "losses":losses/count, "ccwm":ccwm/count, "max_score":max_score/count, "opr":opr/count, "dpr":dpr/count}