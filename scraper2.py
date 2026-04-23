from playwright.sync_api import sync_playwright, Page, Browser, Playwright
from time import sleep
import re
import time
import multiprocessing as mp
import queue
import traceback

class BradescoScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None
        self.timesleep = 2

    def start(self) -> None:
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=500
        )
        self.page = self.browser.new_page()

    def stop(self) -> None:
        print("STOP chamado")
        try:
            if self.browser:
                self.browser.close()
        except Exception as e:
            print(f"Aviso ao fechar browser: {e}")

        try:
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"Aviso ao fechar playwright: {e}")

    def login(self, cpf_cnpj_numero: str, senha: str) -> None:
        if not self.page:
            raise RuntimeError("O navegador não foi iniciado. Chame start() antes.")

        self.page.goto(
            "https://wwwn.bradescoseguros.com.br/pnegocios2/wps/portal/portaldenegociosnovo",
            wait_until="domcontentloaded"
        )
        print("1 - Página aberta")

        self.page.locator("//input[@class='input cpfcnpj']").wait_for(state="visible", timeout=20000)
        self.page.locator("//input[@class='input cpfcnpj']").fill(cpf_cnpj_numero)
        print("2 - CPF/CNPJ preenchido")

        self.page.locator("//button[@id='tag_Home_Login-Continuar']").click()
        print("3 - Clicou em continuar")

        self.page.locator("//label[@for='select-login' and @class='arrow']").wait_for(
            state="visible", timeout=20000
        )
        self.page.locator("//label[@for='select-login' and @class='arrow']").click()
        print("4 - Abriu seletor")

        self.page.locator("//input[@id='senha']").wait_for(state="visible", timeout=20000)
        self.page.locator("//input[@id='senha']").fill(senha)
        print("5 - Senha preenchida")

        self.page.locator("//button[@id='tag_Home_Login-entrar']").click()
        print("6 - Clicou em entrar")

        self.page.wait_for_timeout(10000)
        print("7 - Esperou 10 segundos após login")

    def clicar_re(self) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        print("8 - Tentando clicar em RE")
        link_re = self.page.locator("a#re")
        link_re.wait_for(state="visible", timeout=15000)
        link_re.click()
        print("9 - Clicou em RE")

        self.page.wait_for_timeout(10000)
        print("10 - Esperou 10 segundos após clicar em RE")
    
    def fechar_popup(self) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        print("60 - Tentando fechar pop-up")

        try:
            modal = self.page.locator("div.modal[role='dialog']:visible").last
            botao = modal.locator("div.modal-header button.close")

            modal.wait_for(state="visible", timeout=5000)
            botao.wait_for(state="visible", timeout=5000)
            botao.scroll_into_view_if_needed()
            botao.click(force=True)

            print("61 - Pop-up fechado")
            self.page.wait_for_timeout(2000)
            sleep(self.timesleep)

        except Exception:
            print("61 - Pop-up não apareceu ou não foi possível fechar. Seguindo o fluxo...")
            pass
    
    def aceitar_cookies(self) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        print("62 - Tentando aceitar cookies")

        try:
            botao = self.page.locator("button#adopt-accept-all-button")
            botao.wait_for(state="visible", timeout=5000)
            botao.scroll_into_view_if_needed()
            botao.click(force=True)

            print("63 - Cookies aceitos")
            self.page.wait_for_timeout(2000)

        except Exception:
            print("63 - Banner de cookies não apareceu ou não foi possível clicar. Seguindo o fluxo...")
            pass
        

    def clicar_cotacoes(self) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        spans = self.page.locator("span")
        alvo = spans.filter(has_text="Cotações").first
        alvo.wait_for(state="visible", timeout=15000)
        alvo.click()

    def clicar_residencial_sob_medida(self) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        cards = self.page.locator("div.cursor-pointer")
        alvo = cards.filter(has_text="Residencial Sob Medida").first
        alvo.wait_for(state="visible", timeout=15000)
        alvo.click()
        sleep(self.timesleep)

    def preencher_valor_imovel(self, valor: str = "500000") -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        print("14 - Tentando preencher valor do imóvel")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("input#formCotacao\\:IVlrImovel")

        campo.wait_for(state="visible", timeout=30000)
        campo.click()
        self.page.wait_for_timeout(500)
        campo.press("Control+A")
        campo.type(valor, delay=200)
        campo.press("Tab")

        print("15 - Valor do imóvel preenchido")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)
    
    def selecionar_tipo_imovel(self, tipo: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        tipo_normalizado = tipo.strip().lower()
        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")

        print(f"16 - Tentando selecionar tipo de imóvel: {tipo}")

        if tipo_normalizado == "casa" or tipo_normalizado == "casa_em_condomínio":
            alvo = frame.locator("label[for='formCotacao:ITipoImovel:0']")
        elif tipo_normalizado == "apartamento":
            alvo = frame.locator("label[for='formCotacao:ITipoImovel:1']")
        else:
            raise ValueError("Tipo inválido. Use 'casa' ou 'apartamento'.")

        alvo.wait_for(state="visible", timeout=20000)
        alvo.click()

        print(f"17 - Tipo de imóvel selecionado: {tipo}")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def selecionar_tipo_residencia(self, tipo: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        tipo_normalizado = tipo.strip().lower()
        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")

        print(f"16 - Tentando selecionar tipo de residência: {tipo}")

        if tipo_normalizado == "habitual":
            alvo = frame.locator("label[for='formCotacao:ITipoResidencia:0']")
        elif tipo_normalizado == "habitual desocupada":
            alvo = frame.locator("label[for='formCotacao:ITipoResidencia:1']")
        elif tipo_normalizado == "veraneio":
            alvo = frame.locator("label[for='formCotacao:ITipoResidencia:2']")
        elif tipo_normalizado == "veraneio desocupada":
            alvo = frame.locator("label[for='formCotacao:ITipoResidencia:3']")
        else:
            raise ValueError(
                "Tipo inválido. Use: 'habitual', 'habitual desocupada', 'veraneio' ou 'veraneio desocupada'."
            )

        alvo.wait_for(state="visible", timeout=20000)
        alvo.click()

        print(f"17 - Tipo de residência selecionado: {tipo}")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def selecionar_casa_em_condominio(self, opcao: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        opcao_normalizada = opcao.strip().lower()
        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        select = frame.locator("select#formCotacao\\:IImovelAtividade")

        print(f"18 - Tentando selecionar Casa em Condomínio: {opcao}")

        select.wait_for(state="visible", timeout=30000)

        if opcao_normalizada == "sim":
            select.select_option(value="1")
        elif opcao_normalizada in ("nao", "não"):
            select.select_option(value="2")
        else:
            raise ValueError("Opção inválida. Use 'sim' ou 'nao'.")

        self.page.wait_for_timeout(3000)
        print(f"19 - Casa em Condomínio selecionado: {opcao}")
        sleep(self.timesleep)

    def selecionar_tipo_apartamento(self, tipo_imovel: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        select = frame.locator("select#formCotacao\\:IImovelAtividade")

        print(f"20 - Tentando selecionar Tipo do Imóvel: {tipo_imovel}")

        select.wait_for(state="visible", timeout=30000)
        select.select_option(label=tipo_imovel)

        self.page.wait_for_timeout(3000)
        print(f"21 - Tipo do Imóvel selecionado: {tipo_imovel}")
        sleep(self.timesleep)
    

    def selecionar_tipo_cliente(self, tipo: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        tipo_normalizado = tipo.strip().lower()
        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        select = frame.locator("select#formCotacao\\:ITipoCliente")

        print(f"20 - Tentando selecionar tipo de cliente: {tipo}")
        select.wait_for(state="visible", timeout=30000)

        mapa = {
            "tradicional": "1",
            "tradicional(nao correntista)": "1",
            "tradicional(não correntista)": "1",
            "varejo": "2",
            "prime": "3",
            "principal": "7",
            "empresas": "4",
            "corporate": "5",
        }

        valor = mapa.get(tipo_normalizado)
        if not valor:
            raise ValueError(
                "Tipo inválido. Use: tradicional, varejo, prime, principal, empresas ou corporate."
            )

        select.select_option(value=valor)

        print(f"21 - Tipo de cliente selecionado: {tipo}")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)
    
    def clicar_continuar(self) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        botao = frame.locator("a#formCotacao\\:btnContinuarInclusao")

        print("22 - Tentando clicar em Continuar")
        botao.wait_for(state="visible", timeout=30000)
        botao.click()

        print("23 - Clicou em Continuar")
        self.page.wait_for_timeout(5000)
        sleep(self.timesleep)

    def selecionar_sucursal(self, sucursal: str = "919 - RIB PRETO MERC") -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        select = frame.locator("select#formCotacao\\:ISucursalCombo")

        print(f"24 - Tentando selecionar sucursal: {sucursal}")
        select.wait_for(state="visible", timeout=30000)
        select.select_option(label=sucursal)

        print(f"25 - Sucursal selecionada: {sucursal}")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def selecionar_codigo_cpd(self, codigo: str = "495847") -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        select = frame.locator("select#formCotacao\\:ICodCorretorCombo")

        print(f"26 - Tentando selecionar Código CPD: {codigo}")
        select.wait_for(state="visible", timeout=30000)
        select.select_option(value=codigo)

        print(f"27 - Código CPD selecionado: {codigo}")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)
    
    def preencher_nome_contato(self, nome: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("input#formCotacao\\:IContato")

        print(f"52 - Tentando preencher Nome Contato: {nome}")
        campo.wait_for(state="visible", timeout=30000)
        campo.click()
        campo.press("Control+A")
        campo.fill(nome)
        campo.press("Tab")

        print("53 - Nome Contato preenchido")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_telefone_celular(self, telefone: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("input#formCotacao\\:ITelefoneContato")

        print(f"28 - Tentando preencher Telefone Celular: {telefone}")
        campo.wait_for(state="visible", timeout=30000)
        campo.click()
        campo.press("Control+A")
        campo.fill(telefone)
        campo.press("Tab")

        print("29 - Telefone Celular preenchido")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_email(self, email: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("input#formCotacao\\:IEmailContato")

        print(f"30 - Tentando preencher E-mail: {email}")
        campo.wait_for(state="visible", timeout=30000)
        campo.click()
        campo.press("Control+A")
        campo.fill(email)
        campo.press("Tab")

        print("31 - E-mail preenchido")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_cpf_cnpj_proponente(self, documento: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("input#formCotacao\\:ICpfCnpjProponente")

        print(f"32 - Tentando preencher CPF/CNPJ do Proponente: {documento}")
        campo.wait_for(state="visible", timeout=30000)
        campo.click()
        campo.press("Control+A")
        campo.fill(documento)
        campo.press("Tab")

        print("33 - CPF/CNPJ do Proponente preenchido")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_cep(self, cep: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("input#formCotacao\\:ICepER")

        print(f"34 - Tentando preencher CEP: {cep}")
        campo.wait_for(state="visible", timeout=30000)
        campo.click()
        campo.press("Control+A")
        campo.fill(cep)
        campo.press("Tab")

        print("35 - CEP preenchido")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_numero(self, numero: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("input#formCotacao\\:INumeroER")

        print(f"36 - Tentando preencher Número: {numero}")
        campo.wait_for(state="visible", timeout=30000)
        campo.click()
        campo.press("Control+A")
        campo.fill(numero)
        campo.press("Tab")

        print("37 - Número preenchido")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_tipo_seguro(self, valor: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("select#formCotacao\\:ITipoSeguro")

        print(f"38 - Tentando selecionar Tipo de Seguro: {valor}")
        campo.wait_for(state="visible", timeout=30000)
        campo.select_option(value=valor)

        print("39 - Tipo de Seguro selecionado")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_construcao_alvenaria_imovel(self, texto: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("select#formCotacao\\:IConstrucaoAlvenariaImovel")

        print(f"40 - Tentando selecionar Construção de Alvenaria: {texto}")
        campo.wait_for(state="visible", timeout=30000)
        campo.select_option(label=texto)

        print("41 - Construção de Alvenaria selecionada")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)
    
    def preencher_objeto_seguro(self, texto: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("select#formCotacao\\:IObjetoSeguro")

        print(f"42 - Tentando selecionar Objeto do Seguro: {texto}")
        campo.wait_for(state="visible", timeout=30000)
        campo.select_option(label=texto)

        print("43 - Objeto do Seguro selecionado")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_assistencia_24h(self, texto: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("select#formCotacao\\:IAssist24hs")

        print(f"44 - Tentando selecionar Assistência 24 Horas: {texto}")
        campo.wait_for(state="visible", timeout=30000)
        campo.select_option(label=texto)

        print("45 - Assistência 24 Horas selecionada")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)
    
    def preencher_resid_home_office(self, opcao: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")

        print(f"46 - Tentando selecionar Home Office: {opcao}")

        opcao_normalizada = opcao.strip().lower()

        if opcao_normalizada == "sim":
            seletor = "input[name='formCotacao:j_id764:0:radio__'][value='1']"
        elif opcao_normalizada in ("não", "nao"):
            seletor = "input[name='formCotacao:j_id764:0:radio__'][value='2']"
        else:
            raise ValueError("Opção inválida. Use 'Sim' ou 'Não'.")

        campo = frame.locator(seletor)

        campo.wait_for(state="attached", timeout=30000)
        campo.scroll_into_view_if_needed()

        campo.evaluate("""
            el => {
                el.click();
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        """)

        print("47 - Home Office selecionado")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_resid_atividade_comercial(self, opcao: str) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")

        print(f"48 - Tentando selecionar Atividade Comercial: {opcao}")

        opcao_normalizada = opcao.strip().lower()

        if opcao_normalizada == "sim":
            seletor = "input[name='formCotacao:j_id764:1:radio__'][value='1']"
        elif opcao_normalizada in ("não", "nao"):
            seletor = "input[name='formCotacao:j_id764:1:radio__'][value='2']"
        else:
            raise ValueError("Opção inválida. Use 'Sim' ou 'Não'.")

        campo = frame.locator(seletor)

        campo.wait_for(state="attached", timeout=30000)
        campo.scroll_into_view_if_needed()
        campo.evaluate("""
            el => {
                el.click();
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        """)

        print("49 - Atividade Comercial selecionada")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def preencher_comissao(self, percentual: int | float) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        if percentual < 0.01 or percentual > 50:
            raise ValueError("A comissão deve estar entre 0.01 e 50.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("select#formCotacao\\:IComissao")

        print(f"54 - Tentando selecionar Comissão: {percentual}%")
        campo.wait_for(state="visible", timeout=30000)

        if float(percentual) == 0.01:
            valor = "0.01"
        else:
            valor = f"{float(percentual):.1f}"

        campo.select_option(value=valor)

        print("55 - Comissão selecionada")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def clicar_botao_calcular(self) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        botao = frame.locator("a#formCotacao\\:btnCalcular")

        print("50 - Tentando clicar no botão Calcular")
        botao.wait_for(state="visible", timeout=30000)
        botao.click()

        print("51 - Botão Calcular clicado")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)
        
    def obter_valor_oferta(self, timeout: int = 120000, valor_anterior: str | None = None) -> str:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        print("56 - Aguardando valor da oferta aparecer...")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        campo = frame.locator("span#formCotacao\\:planosOfertas h1.valorTextoDestaque").first

        campo.wait_for(state="visible", timeout=timeout)

        fim = time.time() + (timeout / 1000)

        while time.time() < fim:
            valor = campo.text_content()

            if valor:
                valor = valor.strip()

                if re.fullmatch(r"\d+(?:\.\d{3})*,\d{2}", valor):
                    if valor_anterior is None:
                        print(f"57 - Valor da oferta obtido: {valor}")
                        return valor

                    if valor != valor_anterior:
                        print(f"57 - Valor da oferta atualizado: {valor}")
                        return valor

                    print(f"56.1 - Valor ainda não atualizou. Atual: {valor} | Anterior: {valor_anterior}")

            self.page.wait_for_timeout(1000)

        raise TimeoutError("O valor da oferta não apareceu ou não mudou em até 2 minutos.")

    
    def clicar_botao_recalcular(self) -> None:
        if not self.page:
            raise RuntimeError("A página não foi iniciada. Chame start() antes.")

        frame = self.page.frame_locator("iframe#bspn-iframe-url-crypt-v2")
        botao = frame.locator("a#formCotacao\\:btnCalcular")

        print("58 - Tentando clicar no botão Recalcular")
        botao.wait_for(state="visible", timeout=30000)
        botao.scroll_into_view_if_needed()
        botao.click(force=True)

        print("59 - Botão Recalcular clicado")
        self.page.wait_for_timeout(3000)
        sleep(self.timesleep)

    def converter_valor_brl_para_float(self,valor: str) -> float:
        if not valor or not isinstance(valor, str):
            raise ValueError(f"Valor inválido para conversão: {valor}")

        valor_limpo = valor.strip().replace(".", "").replace(",", "")
        return float(valor_limpo[:-2] + "." + valor_limpo[-2:])
    

#######################################################################################
# Timeout Global
#######################################################################################


def _worker_run_scraper(data, result_queue):
    try:
        resultado = run_scraper(data)
        result_queue.put({
            "ok": True,
            "resultado": resultado
        })
    except Exception as e:
        result_queue.put({
            "ok": False,
            "erro": str(e),
            "traceback": traceback.format_exc()
        })


def run_scraper_com_timeout(data, timeout_segundos: int = 240):
    result_queue = mp.Queue()
    processo = mp.Process(
        target=_worker_run_scraper,
        args=(data, result_queue),
        daemon=True
    )

    processo.start()
    processo.join(timeout_segundos)

    if processo.is_alive():
        print(f"Tempo limite de {timeout_segundos}s excedido. Encerrando processo...")
        processo.terminate()
        processo.join(10)

        if processo.is_alive():
            print("Processo ainda vivo após terminate(). Forçando kill...")
            processo.kill()
            processo.join()

        raise TimeoutError(f"O scraper excedeu o tempo máximo de {timeout_segundos} segundos.")

    try:
        resposta = result_queue.get_nowait()
    except queue.Empty:
        raise RuntimeError("O processo terminou sem retornar resultado.")

    if resposta["ok"]:
        return resposta["resultado"]

    raise RuntimeError(
        f'Erro no scraper: {resposta["erro"]}\n\n{resposta["traceback"]}'
    )



def run_scraper(data):
    scraper = BradescoScraper()  # troque pelo nome real da sua classe

    try:
        scraper.start()
        scraper.login(
            cpf_cnpj_numero=data.cpf_cnpj_login,
            senha=data.senha
        )

        scraper.clicar_re()
        scraper.fechar_popup()
        scraper.aceitar_cookies()
        scraper.clicar_cotacoes()
        scraper.clicar_residencial_sob_medida()

        if data.valor_imovel:
            scraper.preencher_valor_imovel(data.valor_imovel)
        else:
            scraper.preencher_valor_imovel()

        scraper.selecionar_tipo_imovel(data.tipo_imovel)
        scraper.selecionar_tipo_residencia(data.tipo_residencia)

        if data.tipo_imovel.strip().lower() == "casa_em_condomínio":
            #if not data.casa_em_condominio:
            #    raise ValueError("Para tipo_imovel='casa', informe casa_em_condominio.")
            scraper.selecionar_casa_em_condominio("sim")
        elif data.tipo_imovel.strip().lower() == "casa":
            scraper.selecionar_casa_em_condominio("nao")
        else:
            #if not data.tipo_apartamento:
            #    raise ValueError("Para imóvel diferente de casa, informe tipo_apartamento.")
            scraper.selecionar_tipo_apartamento("APARTAMENTO (PAVIMENTO SUPERIOR)")

        scraper.selecionar_tipo_cliente(data.tipo_cliente)
        scraper.clicar_continuar()
        scraper.selecionar_sucursal(data.sucursal)
        scraper.selecionar_codigo_cpd(data.codigo_cpd)
        scraper.preencher_nome_contato(data.nome_contato)
        scraper.preencher_telefone_celular(data.telefone_celular)
        scraper.preencher_email(data.email)
        scraper.preencher_cpf_cnpj_proponente(data.cpf_cnpj_proponente)
        scraper.preencher_cep(data.cep)
        scraper.preencher_numero(data.numero)
        scraper.preencher_tipo_seguro(data.tipo_seguro)
        scraper.preencher_construcao_alvenaria_imovel(data.construcao_alvenaria_imovel)
        scraper.preencher_objeto_seguro(data.objeto_seguro)
        scraper.preencher_assistencia_24h(data.assistencia_24h_inicial)
        scraper.preencher_resid_home_office(data.resid_home_office)
        scraper.preencher_resid_atividade_comercial(data.resid_atividade_comercial)
        scraper.preencher_comissao(data.comissao)

        scraper.clicar_botao_calcular()
        valor_1 = scraper.obter_valor_oferta()

        valor_2 = None
        if data.assistencia_24h_recalculo:
            scraper.preencher_assistencia_24h(data.assistencia_24h_recalculo)
            scraper.clicar_botao_recalcular()
            valor_2 = scraper.obter_valor_oferta(valor_anterior=valor_1)

        valor_3 = None
        if data.assistencia_24h_recalculo_2:
            valor_anterior = valor_2 if valor_2 is not None else valor_1
            scraper.preencher_assistencia_24h(data.assistencia_24h_recalculo_2)
            scraper.clicar_botao_recalcular()
            valor_3 = scraper.obter_valor_oferta(valor_anterior=valor_anterior)

        return {
            "valor_inicial": scraper.converter_valor_brl_para_float(valor_1),
            "valor_recalculado": scraper.converter_valor_brl_para_float(valor_2) if valor_2 is not None else None,
            "valor_recalculado_2": scraper.converter_valor_brl_para_float(valor_3) if valor_3 is not None else None
        }

    finally:
        print("Entrou no finally")
        scraper.stop()


if __name__ == "__main__":
    print("Execute este arquivo via FastAPI ou importe run_scraper().")