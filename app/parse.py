import string, requests

def parse_url(url):
    output_text = ""
    deaths = 0
    antags = []

    r = requests.get(url)

    if r.status_code != 200:
        return make_response("ERROR", 500)
    else:
        lines = r.iter_lines()
        for line in lines:
            x = line.decode("utf-8")
            x = x.split('|')
            if x[0] == "MOB_DEATH":
                deaths += 1
            elif x[0] == "ANTAG_OBJ":
                antags.append(x[1] + " the " + x[3])

        output_text += "Number of mobs dead: " + str(deaths) + "\n"
        output_text += "Antags: \n"

        for antag in antags:
            output_text += antag + "\n"

        return output_text

def parse_line(line):
    return null
