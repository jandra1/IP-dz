''' 
Domaća zadaća iz kolegija Interpretacija programa.
Napravili: Ivona Čižić, Barbara Posavec, Luka Jandrijević


TODO: - osmislit novi konačni ili beskonačni tip podatka koji nije uobičajen u drugim programskim jezicima
	  - unarne, binarne, terarne operatore nad tim tipom
	  - implicitno pretvaranje među tipovima
'''

from vepar import *

class T(TipoviTokena):
	PRINT, IF, ELSE, THEN= 'print', 'if', 'else', 'then' 
	ENDIF, NEWLINE = 'endif', 'newline'
	OTV, ZATV, TOČKAZAREZ, PLUS, MINUS, PUTA, KROZ, MANJE, VEĆE, JEDNAKO = '();+-*/<>='
	MANJEJ, VEĆEJ, JEDNAKOJ, RAZLIČITO = '<=','>=', '==', '!='
	NAVODNICI, RETURN, CALL, DEF, INPUT = '"', 'return', 'call', 'def', 'inpt'
	VOTV, VZATV, ZAREZ = '{},'
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
# broj -> aritm usporedba aritm | aritm 
# usporedba -> MANJE | VEĆE | MANJEJ | VEĆEJ | JEDNAKOJ | RAZLIČITO
# aritm -> član | aritm PLUS član | aritm MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> BROJ | IME | funkcija_zovi | MINUS faktor | OTV broj ZATV
# poziv -> OTV ZATV | OTV argumenti ZATV
# argumenti -> argument | argumenti ZAREZ argument
# argument -> aritm | [!KONTEKST] - potrebno za rekurziju


###TODO: provjerit BKG jel dobra

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
		p >> JEDNAKO
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
		if p >= P.ELSE:
			onda = p.naredbe_lista()
		p >> T.ENDIF
		return If(uvjet, onda, inače)

	def inpt(p) -> 'Inpt':
		p >> T.INPUT
		return Inpt(p >> T.IME)


	def broj(p) -> 'Usporedba|aritm':
		prvi = p.aritm()
		usporedba = {T.MANJE, T.MANJEJ, T.VEĆE, T.VEĆEJ, T.JEDNAKOJ, T.RAZLIČITO}
		manje = veće = jednako = nenavedeno
		if p > usporedba:
			while u := p >= usporedba:
				if u ^ T.MANJE: 
					manje = u
				elif u ^ T.VEĆE: 
					veće = u
				elif u ^ T.JEDNAKO: 
					jednako = u
				return Usporedba(prvi, p.aritm(), manje, veće, jednako)
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
			zagrada = p.aritm()
			p >> T.ZATV
			return zagrada
		else: return p >> {T.BROJ, T.IME}



class Program(AST): pass
class Pridruži(AST): pass
class If(AST): pass
class Print(AST): pass



test = '''#ovo je komentar

asdasdasd#
//jednolinijski komentar
print "neki tekst";
exprs = 1 + 3/4 <= 1 >= > = ==  
//sve radi kako treba za sada
'''

ParsTest = '''
print NEWLINE;
print "ovo je string";
print 3+5;
'''

snail(test)
#P(ParsTest)
#prikaz(ParsTest)


