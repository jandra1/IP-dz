''' 
Domaća zadaća iz kolegija Interpretacija programa.
Napravili: Ivona Čižić, Barbara Posavec, Luka Jandrijević

'''

from vepar import *

class T(TipoviTokena):
	PRINT, IF, ELSE, THEN= 'print', 'if', 'else', 'then' 
	ENDIF, NEWLINE = 'endif', 'newline'
	OTV, ZATV, TOČKAZAREZ, PLUS, MINUS, PUTA, KROZ, MANJE, VEĆE, JEDNAKO = '();+-*/<>='
	MANJEJ, VEĆEJ, JEDNAKOJ, RAZLIČITO = '<=','>=', '==', '!='
	NAVODNICI = '"'
	class BROJ(Token):
		#def vrijednost(self): return
		pass
	class IME(Token):
		#def vrijednost(self): return
		pass

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
		elif znak.isalpha():
			lex * str.isalnum
			yield lex.literal_ili(T.IME)
		elif znak.isdecimal():
			lex.prirodni_broj(znak)
			yield lex.token(T.BROJ)
		elif znak == '\\':
			if lex >= '\\': 
				lex - '\n'
				lex.zanemari()
		# ako naiđe na znak '#' onda zanemari sav tekst dok ne pročita ponovno znak '#'
		elif znak == '#':
			lex.pročitaj_do('#', uključivo=True, više_redova=True)
			lex.zanemari()
		else: yield lex.literal(T)

test = '''#ovo je komentar

asdasdasd#
a = 3+5 - /  !=   
'''



snail(test)


