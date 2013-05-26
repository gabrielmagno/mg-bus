# -- encoding: utf-8 --

import re
import json
import urllib
import time
import datetime

# Belo Horizonte

def coleta_lista_linhas_bht():
    html = urllib.urlopen("http://servicosbhtrans.pbh.gov.br/bhtrans/servicos_eletronicos/transporte_qh_info.asp").read()
    linhas = re.findall("<a rel=\'external\' href=\"transporte_qh_resultado\.asp\?linha=([^\"]+)\" data-transition=\"slide\">", html)
    return linhas


def coleta_info_linha_bht(linha_busca):
    
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
                minutos_dados.append([int(minuto), ("E" if len(tipo) > 0 else "")])
            sublinha_horarios.append([hora, minutos_dados])
        linha_info["horarios"].append([sublinha_nome, sublinha_horarios])

    return linha_info


def imprime_info_linha_bht(linha_busca):
    linha_info = coleta_info_linha_bht(linha_busca)
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


def coleta_infos_bht():
    infos = {}
    infos["coletado"] = int(time.time())
    infos["linhas"] = {}
    linhas = coleta_lista_linhas_bht()
    for linha in linhas:
        print "- Coletando %s" % (linha)
        infos["linhas"][linha] = coleta_info_linha_bht(linha)
    outfile = open("onibus_bht-%s.json" % (datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")), "w")
    json.dump(infos, outfile)
    outfile.close()



# DER

def coleta_lista_linhas_der():
    html = urllib.urlopen("http://200.198.22.36/html/transp_rmbh/novo_site/IndexNovo.asp").read()
    data_atualizacao = re.search("<input type=\"hidden\" name=\"DataAtualizacao\" value=\"([^\"]+)\">", html).group(1)
    linhas = [linha.decode("latin1") for linha in re.findall("<option value=\"([^\"]+)\">", html)]
    return linhas, data_atualizacao


def coleta_info_linha_der(linha_consulta, data_atualizacao):

    linha_info = {}

    post_data = urllib.urlencode({"DataAtualizacao":data_atualizacao, "Escolha":linha_consulta.encode("latin1"), "Linha":"", "Opcao":"H"})
    html = urllib.urlopen("http://200.198.22.36/html/transp_rmbh/novo_site/Detalhe2.asp?%s" % (post_data)).read()

    busca_numero = re.search("<td width=\"\d+%\" align=\"right\">Linha:</td>\s+<td width=\"\d+%\">([^<]+)</td>", html, re.DOTALL)
    busca_tarifa = re.search("<td width=\"\d+%\" align=\"right\">Tarifa:</td>\s+<td width=\"\d+%\">R\$ ([^<]+)</td>", html, re.DOTALL)
    busca_nome = re.search("<td width=\"\d+%\" align=\"right\">Descri..o:</td>\s+<td width=\"\d+%\" colspan=\"\d+\">([^<]+)</td>", html, re.DOTALL)
    busca_empresa = re.search("<td width=\"\d+%\" align=\"right\">Empresa:</td>\s+<td width=\"\d+%\" colspan=\"\d+\">([^<]+)</td>", html, re.DOTALL)
    busca_municipio = re.search("<td width=\"\d+%\" align=\"right\">Munic.pio:</td>\s+<td width=\"\d+%\" colspan=\"\d+\">([^<]+)</td>", html, re.DOTALL)
    busca_sublinhas = re.findall("<table.*?class=\"Mtable\">.*?<tr bgcolor=\"#A9A79E\">.*?<font color=\"#FFFFFF\">Hor.rio ([^<]+)</font></td>.*?<tr bgcolor=\"#DCDCD8\">(.+?)</tr>\s+(<tr bgcolor=\'#FFFFFF\'>.+?)</tr>\s+</table>", html, re.DOTALL)

    linha_info["numero"] = busca_numero.group(1)
    linha_info["tarifa"] = float(busca_tarifa.group(1).replace(",", "."))
    linha_info["nome"] = busca_nome.group(1).decode("latin1")
    linha_info["empresa"] = busca_empresa.group(1).decode("latin1")
    linha_info["municipio"] = busca_municipio.group(1).decode("latin1")

    linha_info["horarios"] = []
    for sublinha_nome, sublinha_horas_html, sublinha_minutos_html in busca_sublinhas:
        horas = map(int, re.findall("<td align=\"center\"\s+width=\"\d+%\"><font color=\"#31302A\">(\d+)</font></td>", sublinha_horas_html))
        blocos_minutos_html = re.findall("<tr bgcolor='#FFFFFF'>(.*?)</tr>", sublinha_minutos_html, re.DOTALL)
        horarios = {hora:[] for hora in horas}
        for bloco_minutos_html in blocos_minutos_html:
            minutos_html = re.findall("<td align=\'center\'><font color=\'#000000\'>(.*?)</font>", bloco_minutos_html)
            for hora, minuto_html in enumerate(minutos_html):
                busca_tipo = re.search("<a.*?>(\d+)(\w+)</a>", minuto_html)
                if busca_tipo:
                    horarios[hora].append([int(busca_tipo.group(1)), busca_tipo.group(2)])
                elif len(minuto_html):
                    horarios[hora].append([int(minuto_html), ""])
        sublinha_horarios = [[hora, horarios[hora]] for hora in xrange(24)]
        linha_info["horarios"].append([sublinha_nome.decode("latin1"), sublinha_horarios])

    return linha_info


def imprime_info_linha_der(linha_busca, data_atualizacao):
    linha_info = coleta_info_linha_der(linha_busca, data_atualizacao)
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

def coleta_infos_der():
    infos = {}
    infos["coletado"] = int(time.time())
    linhas, data_atualizacao = coleta_lista_linhas_der()
    infos["atualizado"] = data_atualizacao
    infos["linhas"] = {}
    for linha in linhas:
        print "- Coletando %s" % (linha)
        infos["linhas"][linha] = coleta_info_linha_der(linha, data_atualizacao)
    outfile = open("onibus_der-%s.json" % (datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")), "w")
    json.dump(infos, outfile)
    outfile.close()



if __name__ == "__main__":

    coleta_infos_bht()
    #coleta_infos_der()


