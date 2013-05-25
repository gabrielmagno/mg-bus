# -- encoding: utf-8 --

import re
import json
import urllib
import time
import datetime


def coleta_lista_linhas_belohorizonte():
    html = urllib.urlopen("http://servicosbhtrans.pbh.gov.br/bhtrans/servicos_eletronicos/transporte_qh_info.asp").read()
    linhas = re.findall("<a rel=\'external\' href=\"transporte_qh_resultado\.asp\?linha=([^\"]+)\" data-transition=\"slide\">", html)
    return linhas


def coleta_info_linha_belohorizonte(linha_busca):
    
    linha_info = {}

    html = urllib.urlopen("http://servicosbhtrans.pbh.gov.br/bhtrans/servicos_eletronicos/transporte_qh_resultado.asp?linha=%s" % (linha_busca)).read()
    
    busca_linhaonibus = re.search("<div class=\"linhaOnibus\"> <img src=\"[^\"]+\" alt=\"[^\"]+\" class=\"left2\" />\s+<h1>Linha(.+?)<br />(.+?)</h1>", html, re.DOTALL)
    busca_tarifa = re.search("<div class=\"descricao\">\s+<p><span>TARIFA: </span>R\$([^<]+)</p>", html, re.DOTALL)
    busca_concessionario = re.search("<p><span>CONCESSION..RIO:</span></p>\s+<p>(.+?)</p>", html, re.DOTALL)
    busca_sublinhas = re.findall("onclick=\"switchMenu\(\'([^\']+)\',this\);\"  /></a><b>&nbsp;([^<]+)</b> </td>", html, re.DOTALL)

    linha_info["numero"] = busca_linhaonibus.group(1).strip() if busca_linhaonibus is not None else None
    linha_info["nome"] = busca_linhaonibus.group(2).strip() if busca_linhaonibus is not None else None
    linha_info["tarifa"] = float(busca_tarifa.group(1).strip().replace(",", ".")) if busca_tarifa is not None else None
    linha_info["concessionario"] = re.sub("[\n\r ]+", " ", busca_concessionario.group(1).replace("&nbsp;", "")).replace("<br /> ", "\n").strip() if busca_concessionario is not None else None

    linha_info["horarios"] = []
    sublinhas = [(sl_id, re.sub("[\n\r ]+", " ", sl_nome).strip()) for sl_id, sl_nome in busca_sublinhas]
    for sublinha_id, sublinha_nome in sublinhas:
        sublinha_html = re.search("<div id=\"%s\" style=\" display:none\" >(.*?)</table>" % (sublinha_id.replace("(", "\(").replace(")", "\)")), html, re.DOTALL).group(1)
        horas = map(int, re.findall("<td class=\"celHoras\" > (\d+) </td>", sublinha_html))
        horas_minutos_html = re.findall("<td width=\'4%\' class=\'celMinutos\'>(.*?)</td>", sublinha_html)
        sublinha_horarios = []
        for hora, minutos_html in zip(horas, horas_minutos_html[1:]):
            minutos = re.findall("<a (class=\'color\' )?href=\'[^\']+\'>(\d+)</a>", minutos_html)
            minutos_dados = []
            for tipo, minuto in minutos:
                minutos_dados.append([int(minuto), (True if len(tipo) > 0 else False)])
            sublinha_horarios.append([hora, minutos_dados])
        linha_info["horarios"].append([sublinha_nome, sublinha_horarios])

    return linha_info


def imprime_info_linha_belohorizonte(linha_busca):
    linha_info = coleta_info_linha_belohorizonte(linha_busca)
    print "* %s" % (linha_busca)
    print "    + Numero: %s" % (linha_info["numero"])
    print "    + Nome: %s" % (linha_info["nome"])
    print "    + Horarios:"
    for sublinha_nome, horarios in linha_info["horarios"]:
        print "        - %s" % (sublinha_nome)
        for hora, minutos_dados in horarios:
            if len(minutos_dados) > 0:
                print "            |",
                for minuto, tipo in minutos_dados:
                    if tipo:
                        print "%d:%d*" % (hora, minuto),
                    else:
                        print "%d:%d" % (hora, minuto),
                print


def coleta_infos_belohorizonte():
    infos = {}
    infos["atualizado"] = int(time.time())
    infos["linhas"] = {}
    linhas = coleta_lista_linhas_belohorizonte()
    for linha in linhas:
        print "- Coletando %s" % (linha)
        infos["linhas"][linha] = coleta_info_linha_belohorizonte(linha)
    outfile = open("onibus_belohorizonte-%s.json" % (datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")), "w")
    json.dump(infos, outfile)
    outfile.close()



if __name__ == "__main__":

    coleta_infos_belohorizonte()



