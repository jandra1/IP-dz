''' 
Domaća zadaća iz kolegija Interpretacija programa.
Napravili: Ivona Čižić, Barbara Posavec, Luka Jandrijević


TODO: - osmislit novi konačni ili beskonačni tip podatka koji nije uobičajen u drugim programskim jezicima
	  - unarne, binarne, terarne operatore nad tim tipom
	  - implicitno pretvaranje među tipovima


Overleaf link za dokumentaciju: https://www.overleaf.com/3936359378pqggjhqxwqmw

'''

from vepar import *
import fractions

class T(TipoviTokena):
	PRINT, IF, ELSE, THEN= 'print', 'if', 'else', 'then' 
	ENDIF, NEWLINE = 'endif', 'newline'
	OTV, ZATV, TOČKAZAREZ, PLUS, MINUS, PUTA, KROZ, MANJE, VEĆE, JEDNAKO = '();+-*/<>='
	MANJEJ, VEĆEJ, JEDNAKOJ, RAZLIČITO = '<=','>=', '==', '!='
	NAVODNICI, RETURN, CALL, DEF, INPUT = '"', 'return', 'call', 'def', 'inpt'
	VOTV, VZATV, ZAREZ = '{},'
	PLUSP, MINUSM = '++', '--'
	class BROJ(Token):
		def vrijednost(t): return fractions.Fraction(t.sadržaj)
	class IME(Token):
		def vrijednost(t): return rt.memorija[t]
	class TEKST(Token):
		def vrijednost(t): return t.sadržaj[1:-1]


@lexer
def snail(lex):
	for znak in lex:
		if znak.isspace(): lex.zanemari()
		elif znak == '<': yield lex.token(T.MANJEJ if lex >= '=' else T.MANJE)
		elif znak == '>': yield lex.token(T.VEĆEJ if lex >= '=' else T.VEĆE)
		elif znak == '=': yield lex.token(T.JEDNAKOJ if lex >= '=' else T.JEDNAKO)
		elif znak == '+': yield lex.token(T.PLUSP if lex >= '+' else T.PLUS)
		elif znak == '-': yield lex.token(T.MINUSM if lex >= '-' else T.MINUS)
		elif znak == '!':
			if lex >= '=': yield lex.token(T.RAZLIČITO)
			else: raise lex.greška('iza znaka "!" mora slijediti znak "="')
		elif znak == '"':
			lex - '"'
			yield lex.token(T.TEKST)
		elif znak.isalpha():
			lex * str.isalnum
			yield lex.literal_ili(T.IME)
		elif znak.isdecimal():
			lex.prirodni_broj(znak)
			yield lex.token(T.BROJ)
		elif znak == '/':
			if lex >= '/': 
				lex - '\n'
				lex.zanemari()
			else: yield lex.token(T.KROZ)
		# ako naiđe na znak '#' onda zanemari sav tekst dok ne pročita ponovno znak '#'
		elif znak == '#':
			lex.pročitaj_do('#', uključivo=True, više_redova=True)
			lex.zanemari()
		else: yield lex.literal(T)

### BKG za jezik:
# start = program = naredbe_lista -> naredbe | naredbe_lista naredbe 
# naredbe -> pridruži | print_naredba | if_naredba | funkcija_zovi | def_funkcija | inpt
# def_funkcija -> DEF IME OTV parametri ZATV JEDNAKO VOTV naredbe_lista RETURN argument VZATV
# funkcija_zovi -> CALL IME poziv
# parametri -> '' | IME | parametri ZAREZ IME
# inpt -> INPUT IME
# pridruži -> IME JEDNAKO broj TOČKAZAREZ
# print_naredba -> PRINT broj TOČKAZAREZ | PRINT TEKST TOČKAZAREZ | PRINT NEWLINE TOČKAZAREZ 
# if_naredba -> IF broj THEN naredbe_lista ENDIF | IF broj THEN naredbe_lista ELSE naredbe_lista ENDIF
# broj -> aritm usporedba aritm | aritm | aritm unarni
# unarni -> PLUSP | MINUSM
# usporedba -> MANJE | VEĆE | MANJEJ | VEĆEJ | JEDNAKOJ | RAZLIČITO
# aritm -> član | aritm PLUS član | aritm MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> BROJ | IME | funkcija_zovi | MINUS faktor | OTV broj ZATV 
# poziv -> OTV ZATV | OTV argumenti ZATV
# argumenti -> argument | argumenti ZAREZ argument
# argument -> aritm | [!KONTEKST] - potrebno za rekurziju


class P(Parser):
	def start(p) -> 'Program': 
		return Program(p.naredbe_lista())

	def naredbe_lista(p) -> '(pridruži|print_naredba|if_naredba|funkcija_zovi|def_funkcija|inpt)*':
		lista = []
		while ...:
			if p > T.IME: lista.append(p.pridruži())
			elif p > T.PRINT: lista.append(p.print_naredba())
			elif p > T.IF: lista.append(p.if_naredba())
			elif p > T.CALL: lista.append(p.funkcija_zovi())
			elif p > T.DEF: lista.append(p.def_funkcija())
			elif p > T.INPUT: lista.append(p.inpt())
			else: return lista

	def pridruži(p) -> 'Pridruži':
		varijabla = p >> T.IME
		p >> T.JEDNAKO
		pridruženo = p.broj()
		p >> T.TOČKAZAREZ
		return Pridruži(varijabla, pridruženo)

	def print_naredba(p) -> 'Print':
		p >> T.PRINT
		if p > {T.BROJ, T.IME}: tipvar = p.broj()
		elif p > T.NEWLINE: tipvar = p >> T.NEWLINE
		else: tipvar = p >> T.TEKST
		p >> T.TOČKAZAREZ
		return Print(tipvar)

	def if_naredba(p) -> 'If':
		p >> T.IF
		uvjet = p.broj()
		p >> T.THEN
		onda = p.naredbe_lista()
		inače = []
		if p >= T.ELSE:
			inače = p.naredbe_lista()
		p >> T.ENDIF
		return If(uvjet, onda, inače)

	def inpt(p) -> 'Inpt':
		p >> T.INPUT
		return Inpt(p >> T.IME)

	def def_funkcija(p):
		return

	def funkcija_zovi(p): 
		return

	def broj(p) -> 'Usporedba|Unarni|aritm':
		unarni = {T.PLUSP, T.MINUSM}
		prvi = p.aritm()
		usporedba = {T.MANJE, T.MANJEJ, T.VEĆE, T.VEĆEJ, T.JEDNAKOJ, T.RAZLIČITO}
		manje = veće = jednako = većej = manjej = različito = nenavedeno
		plusp = minusm = nenavedeno
		if u := p >= usporedba:
			if u ^ T.MANJE: 
				manje = u
			elif u ^ T.VEĆE: 
				veće = u
			elif u ^ T.JEDNAKOJ: 
				jednako = u
			elif u ^ T.VEĆEJ:
				većej = u
			elif u ^ T.MANJEJ:
				manjej = u
			elif u ^ T.RAZLIČITO:
				različito = u
			return Usporedba(prvi, p.aritm(), manje, veće, jednako, većej, manjej, različito)
		elif k := p >= unarni:
			if k ^ T.PLUSP:
				plusp = k
			else:
				minusm = k
			return Unarni(prvi, plusp, minusm)
		else: 
			return prvi

	def aritm(p) -> 'član|Osnovna':
		t = p.član()
		while op := p >= {T.PLUS, T.MINUS}: t = Osnovna(op, t, p.član())
		return t

	def član(p) -> 'faktor|Osnovna':
		t = p.faktor()
		while op := p >= {T.PUTA, T.KROZ}: t = Osnovna(op, t, p.faktor())
		return t

	def faktor(p) -> 'Suprotan|broj|BROJ|IME':
		if p >= T.MINUS: return Suprotan(p.faktor())
		elif p >= T.OTV:
			zagrada = p.broj()
			p >> T.ZATV
			return zagrada
		else: return p >> {T.BROJ, T.IME}


### AST
# Program: naredbe_lista: [naredbe]
# naredbe_lista: Inpt: varijabla:IME
#				 Pridruži: varijabla:IME što:broj
#				 Print: tipvar:broj|TEKST|NEWLINE
#				 If: uvjet:broj onda:[naredbe_lista] inače:[naredbe_lista]
# broj: Usporedba: lijevo:broj desno: broj
#				   manje: MANJE? veće: VEĆE? jednako: JEDNAKO? manjej: MANJEJ? većej: VEĆEJ? 
#		Unarni: operator: PLUSP|MINUSM izraz: broj
#		Osnovna: operacija:PLUS|MINUS|PUTA|KROZ lijevo:broj desno:broj
#		Suprotan: od: broj
#		BROJ: Token
#		IME: Token


class Program(AST): 
	naredbe_lista: 'naredbe*'
	def izvrši(program):
		rt.memorija = Memorija()
		for naredbe in program.naredbe_lista: naredbe.izvrši()

class Inpt(AST):
	varijabla: 'IME'
	def izvrši(unos):
		v = unos.varijabla
		prompt = f'\t{v.sadržaj}? '
		while ...:
			t = input(prompt)
			try: rt.memorija[v] = fractions.Fraction(t)
			except ValueError: print(end='Ovo nije racionalni broj ')
			else: break


class Pridruži(AST):
	varijabla: 'IME'
	što: 'broj'
	def izvrši(self):
		rt.memorija[self.varijabla] = self.što.vrijednost()

class If(AST): 
	uvjet: 'broj'
	onda: 'naredbe*'
	inače: 'naredbe*'
	def izvrši(grananje):
		b = grananje.uvjet.vrijednost()
		if b == ~0: sljedeći = grananje.onda
		elif b == 0: sljedeći = grananje.inače
		else: raise GreškaIzvođenja('Pogreška u if naredbi')
		for naredba in sljedeći: naredba.izvrši()



class Print(AST):
	tipvar: 'broj|TEKST|NEWLINE'
	def izvrši(ispis):
		if ispis.tipvar ^ T.NEWLINE: print()
		else:
			t = ispis.tipvar.vrijednost()
			if isinstance(t, fractions.Fraction): t = str(t).replace('/', '÷')
			print(t, end=' ')


class Usporedba(AST):
	lijevo: 'broj'
	desno: 'broj'
	manje: 'MANJE?'
	veće: 'VEĆE?'
	jednako: 'JEDNAKOJ?'
	većej: 'VEĆEJ?'
	manjej: 'MANJEJ?'
	različito: 'RAZLIČITO?'
	def vrijednost(self):
		l, d = self.lijevo.vrijednost(), self.desno.vrijednost()
		if ((self.manje and l < d) or (self.jednako and l == d) or (self.veće and l > d) or 
			(self.manjej and l <= d) or (self.većej and l >= d) or (self.različito and l != d)): return 1
		else: return 0

class Osnovna(AST):
	operacija: 'T'
	lijevo: 'broj'
	desno: 'broj'
	def vrijednost(self):
		l, d = self.lijevo.vrijednost(), self.desno.vrijednost()
		o = self.operacija
		if o ^ T.PLUS: return l + d
		elif o ^ T.MINUS: return l - d
		elif o ^ T.PUTA: return l * d
		elif o ^ T.KROZ:
			if d: return fractions.Fraction(l, d)
			else: raise o.iznimka('Nazivnik je nula!')
		else: assert False, f'Nepokrivena binarna operacija {o}'

class Unarni(AST):
	izraz: 'broj'
	plusp: 'PLUSP?'
	minusm: 'MINUSM?'
	def vrijednost(self):
		o = self.izraz.vrijednost()
		if self.plusp != nenavedeno:
			return (o+1)
		else:
			return (o-1)
		
test = '''a = 1;
c = 1+4*(a > 2);
print c;
'''


ParsTest =P('''a = 1;
c = 1+4*(a < 2);
print c;
''')

#snail(test)

prikaz(ParsTest)
ParsTest.izvrši()


