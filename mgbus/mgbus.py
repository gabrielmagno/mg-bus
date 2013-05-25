import re
import urllib

def coleta_tabela_onibus_belohorizonte(linha):
    html = urllib.urlopen("http://servicosbhtrans.pbh.gov.br/bhtrans/servicos_eletronicos/transporte_qh_resultado.asp?linha=%s" % (linha)).read()
    sublinhas = re.findall("<td class=\"tituloTabela\"><a href=\"#\" ><img src=\"[^\"]+\" alt=\"[^\"]+\" border=\"0\" onclick=\"switchMenu\(\'([^\']+)\',this\);\"  /></a><b>&nbsp;([^<]+)</b> </td>", html, re.DOTALL)
    sublinhas = [(sl_id, re.sub("[\n\r ]+", " ", sl_nome).strip()) for sl_id, sl_nome in sublinhas]
    tabela_horarios = []
    for sublinha_id, sublinha_nome in sublinhas:
        sublinha_html = re.search("<div id=\"%s\" style=\" display:none\" >(.*?)</table>" % (sublinha_id), html, re.DOTALL).group(1)
        horas = map(int, re.findall("<td class=\"celHoras\" > (\d+) </td>", sublinha_html))
        horas_minutos_html = re.findall("<td width=\'4%\' class=\'celMinutos\'>(.*?)</td>", sublinha_html)
        horarios = []
        for hora, minutos_html in zip(horas, horas_minutos_html[1:]):
            minutos = re.findall("<a (class=\'color\' )?href=\'[^\']+\'>(\d+)</a>", minutos_html)
            minutos_dados = []
            for tipo, minuto in minutos:
                minutos_dados.append([int(minuto), (True if len(tipo) > 0 else False)])
            horarios.append([hora, minutos_dados])
        tabela_horarios.append([sublinha_nome, horarios])
    return tabela_horarios


def imprime_horarios_onibus_belo_horizonte(linha):
    tabela_horarios = coleta_tabela_onibus_belohorizonte(linha)
    for sublinha_nome, horarios in tabela_horarios:
        print "+ %s" % (sublinha_nome)
        for hora, minutos_dados in horarios:
            if len(minutos_dados) > 0:
                print "    -",
                for minuto, tipo in minutos_dados:
                    if tipo:
                        print "%d:%d*" % (hora, minuto),
                    else:
                        print "%d:%d" % (hora, minuto),
                print

imprime_horarios_onibus_belo_horizonte("4405")
imprime_horarios_onibus_belo_horizonte("S54")
imprime_horarios_onibus_belo_horizonte("SC02")
