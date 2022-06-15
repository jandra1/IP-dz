''' 
Domaća zadaća iz kolegija Interpretacija programa.
Napravili: Ivona Čižić, Barbara Posavec, Luka Jandrijević


TODO: - osmislit novi konačni ili beskonačni tip podatka koji nije uobičajen u drugim programskim jezicima
	  - unarne, binarne, terarne operatore nad tim tipom
	  - unos s tipkovnice u varijable ( napravljeno u 21_BASIC.py )
	  - implicitno pretvaranje među tipovima
'''

from vepar import *

class T(TipoviTokena):
	PRINT, IF, ELSE, THEN= 'print', 'if', 'else', 'then' 
	ENDIF, NEWLINE = 'endif', 'newline'
	OTV, ZATV, TOČKAZAREZ, PLUS, MINUS, PUTA, KROZ, MANJE, VEĆE, JEDNAKO = '();+-*/<>='
	MANJEJ, VEĆEJ, JEDNAKOJ, RAZLIČITO = '<=','>=', '==', '!='
	NAVODNICI, RETURN, CALL, DEF = '"', 'return', 'call', 'def'
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
# naredbe -> pridruži | print_naredba | if_naredba | funkcija_zovi | def_funkcija | unos
# def_funkcija -> DEF IME OTV parametri ZATV JEDNAKO VOTV naredbe_lista RETURN argument VZATV
# parametri -> '' | IME | parametri ZAREZ IME
# unos -> UNOS IME
# pridruži -> IME JEDNAKO broj TOČKAZAREZ
# print_naredba -> PRINT broj TOČKAZAREZ | PRINT TEKST TOČKAZAREZ | PRINT NEWLINE TOČKAZAREZ 
# if_naredba -> IF aritm THEN naredbe_lista ENDIF | IF aritm THEN naredbe_lista ELSE naredbe_lista ENDIF
# broj -> aritm usporedba aritm | aritm 
# usporedba -> MANJE | VEĆE | JEDNAKO | MANJEJ | VEĆEJ | JEDNAKOJ | RAZLIČITO
# aritm -> član | aritm PLUS član | aritm MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> BROJ | IME | CALL IME poziv | MINUS faktor | OTV broj ZATV
# poziv -> OTV ZATV | OTV argumenti ZATV
# argumenti -> argument | argumenti ZAREZ argument
# argument -> aritm | [!KONTEKST] - potrebno za rekurziju


###TODO: provjerit BKG jel dobra

class P(Parser):
	def program(p):		


test = '''#ovo je komentar

asdasdasd#
//jednolinijski komentar
print "neki tekst";
exprs = 1 + 3/4 <= 1 >= > = ==  
//sve radi kako treba za sada
'''



snail(test)


