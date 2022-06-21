''' 
Domaća zadaća iz kolegija Interpretacija programa.
Napravili: Ivona Čižić, Barbara Posavec, Luka Jandrijević


TODO: - implicitno pretvaranje među tipovima


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
	PLUSP, MINUSM, TERNARNI = '++', '--', '?'
	class BROJ(Token):
		def vrijednost(self, mem, unutar): return fractions.Fraction(self.sadržaj)
	class IME(Token):
		def vrijednost(self, mem, unutar): return mem[self]
	class TEKST(Token):
		def vrijednost(self, mem, unutar): return self.sadržaj[1:-1]

	#Konačni tip podatka (-1,0,1), opcija "možda" - koristi se kada nismo sigurni u vrijednost
	class MOŽDA(Token):
		literal = 'možda'
		def vrijednost(self, mem, unutar):
			return -1
	class NE(Token):
		literal = 'ne'
		def vrijednost(self, mem, unutar):
			return 0
	class DA(Token):
		literal = 'da'
		def vrijednost(self, mem, unutar):
			return 1



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
# start = program = funkcija | funkcija program
# naredbe_lista -> naredbe | naredbe_lista TOČKAZAREZ naredbe 
# naredbe -> pridruži | print_naredba | if_naredba | inpt | RETURN argument | VOTV VZATV | VOTV naredbe_lista VZATV
# funkcija -> IME OTV parametri ZATV JEDNAKO VOTV naredbe_lista VZATV
# parametri -> '' | IME | parametri ZAREZ IME
# inpt -> INPUT IME
# pridruži -> IME JEDNAKO broj 
# print_naredba -> PRINT broj | PRINT TEKST | PRINT NEWLINE  
# if_naredba -> IF broj THEN naredbe_lista ENDIF | IF broj THEN naredbe_lista ELSE naredbe_lista ENDIF
# broj -> aritm usporedba aritm | aritm | aritm unarni
# unarni -> PLUSP | MINUSM
# usporedba -> MANJE | VEĆE | MANJEJ | VEĆEJ | JEDNAKOJ | RAZLIČITO
# aritm -> član | aritm PLUS član | aritm MINUS član
# član -> faktor | član PUTA faktor | član KROZ faktor
# faktor -> BROJ | IME | IME poziv | MINUS faktor | OTV broj ZATV | DA | NE | MOŽDA | TERNARNI broj ZAREZ broj ZAREZ broj 
# poziv -> OTV ZATV | OTV argumenti ZATV
# argumenti -> argument | argumenti ZAREZ argument
# argument -> broj | [!KONTEKST] - potrebno za rekurziju


class P(Parser):
	def program(p) -> 'Memorija': 
		p.funkcije = Memorija(redefinicija=False)
		while not p > KRAJ:
			funkcija = p.funkcija()
			p.funkcije[funkcija.ime] = funkcija
		return p.funkcije

	def naredbe_lista(p) -> 'Blok|naredbe':
		p >> T.VOTV
		if p >= T.ZATV: return Blok([])
		n = [p.naredbe()]
		while p >= T.TOČKAZAREZ and not p > T.VZATV: n.append(p.naredbe())
		p >> T.VZATV
		return Blok.ili_samo(n)

	def naredbe(p) -> '(Pridruži|Vrati|print_naredba|if_naredba|inpt)*':
		if p > T.PRINT: return p.print_naredba()
		elif p > T.IF: return p.if_naredba()
		elif p > T.INPUT: return p.inpt()
		elif p > T.VOTV: return p.naredbe_lista()
		elif p >= T.RETURN: return Vrati(p.broj())
		else: 
			varijabla = p.ime()
			p >> T.JEDNAKO
			pridruženo = p.broj()
			return Pridruži(varijabla, pridruženo)
		

	def funkcija(p) -> 'Funkcija':
		atributi = p.imef, p.parametrif = p.ime(), p.parametri()
		p >> T.JEDNAKO
		return Funkcija(*atributi, p.naredbe())

	def ime(p) -> 'IME': return p >> T.IME

	def možda_poziv(p, ime) -> 'Poziv|ime':
		if ime in p.funkcije:
			funkcija = p.funkcije[ime]
			return Poziv(funkcija, p.argumenti(funkcija.parametri))
		elif ime == p.imef:
			return Poziv(nenavedeno, p.argumenti(p.parametrif))
		else: return ime

	def argumenti(p, parametri) -> 'broj':
		arg = []
		p >> T.OTV
		for i, parametar in enumerate(parametri):
			if i: p >> T.ZAREZ
			arg.append(p.broj())
		p >> T.ZATV
		return arg

	def ret(p):
		p >= T.RETURN
		value = p >= T.IME
		return Return(value)


	def print_naredba(p) -> 'Print':
		p >> T.PRINT
		if p > {T.BROJ, T.IME}: tipvar = p.broj()
		elif p > T.NEWLINE: tipvar = p >> T.NEWLINE
		else: tipvar = p >> T.TEKST
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

	def parametri(p) -> 'ime*':
		p >> T.OTV
		if p >= T.ZATV: return []
		param = [p.ime()]
		while p >= T.ZAREZ: param.append(p.ime())
		p >> T.ZATV
		return param

	def broj(p) -> 'Ternarni|Usporedba|Unarni|aritm':
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

	def faktor(p) -> 'Suprotan|možda_poziv|broj|BROJ|IME':
		if p >= T.MINUS: return Suprotan(p.faktor())
		elif p >= T.OTV:
			zagrada = p.broj()
			p >> T.ZATV
			return zagrada
		elif ar := p >= T.IME: return p.možda_poziv(ar)
		elif p >= T.TERNARNI:
			prvi = p.broj()
			p >> T.ZAREZ
			drugi = p.broj()
			p >> T.ZAREZ
			treći = p.broj()
			return Ternarni(prvi, drugi, treći)
		else: return p >> {T.BROJ, T.IME, T.DA, T.MOŽDA, T.NE}

def izvrši(funkcije, *argv):
    print('Program je vratio:', funkcije['main'].pozovi(argv))

### AST
# Funkcija: ime: IME parametri:[IME] tijelo:naredbe_lista
# naredbe_lista: Inpt: varijabla:IME
#				 Pridruži: varijabla:IME što:broj
#				 Print: tipvar:broj|TEKST|NEWLINE
#				 If: uvjet:broj onda:[naredbe_lista] inače:[naredbe_lista]
#				 Vrati: što:izraz
#                Blok: naredbe:[naredbe]
# broj: Usporedba: lijevo:broj desno: broj
#				   manje: MANJE? veće: VEĆE? jednako: JEDNAKO? manjej: MANJEJ? većej: VEĆEJ? 
#		Unarni: operator: PLUSP|MINUSM izraz: broj
#		Osnovna: operacija:PLUS|MINUS|PUTA|KROZ lijevo:broj desno:broj
#		Suprotan: od: broj
#		Poziv: funkcija: Funkcija? argumenti:[broj]
#		BROJ: Token
#		IME: Token

class Suprotan(AST):
	od: 'broj'
	def vrijednost(self, mem, unutar):
		return -self.od.vrijednost(mem, unutar)

class Ternarni(AST):
	prvi: 'IME'
	drugi: 'IME'
	treći: 'IME'
	def vrijednost(self, mem, unutar):
		if self.prvi.vrijednost(mem, unutar) != 0 and self.drugi.vrijednost(mem, unutar) != 0 and self.treći.vrijednost(mem, unutar) != 0:
			return 1
		else: return 0

class Blok(AST):
	naredbe: 'naredba*'
	def izvrši(blok, mem, unutar):
		for naredba in blok.naredbe: naredba.izvrši(mem, unutar)

class Vrati(AST):
	što: 'izraz'
	def izvrši(self, mem, unutar):
		raise Povratak(self.što.vrijednost(mem, unutar))


class Funkcija(AST):
    ime: 'IME'
    parametri: 'IME*'
    tijelo: 'naredba'
    def pozovi(funkcija, argumenti):
        lokalni = Memorija(zip(funkcija.parametri, argumenti))
        try: funkcija.tijelo.izvrši(mem=lokalni, unutar=funkcija)
        except Povratak as exc: return exc.preneseno
        else: raise GreškaIzvođenja(f'{funkcija.ime} nije ništa vratila')

class Poziv(AST):
    funkcija: 'Funkcija?'
    argumenti: 'izraz*'
    def vrijednost(poziv, mem, unutar):
        pozvana = poziv.funkcija
        if pozvana is nenavedeno: pozvana = unutar  # rekurzivni poziv
        argumenti = [a.vrijednost(mem, unutar) for a in poziv.argumenti]
        return pozvana.pozovi(argumenti)

    def za_prikaz(poziv):  # samo za ispis, da se ne ispiše čitava funkcija
        r = {'argumenti': poziv.argumenti}
        if poziv.funkcija is nenavedeno: r['*rekurzivni'] = True
        else: r['*ime'] = poziv.funkcija.ime
        return r


class Inpt(AST):
	varijabla: 'IME'
	def izvrši(unos, mem, unutar):
		v = unos.varijabla
		prompt = f'\t{v.sadržaj}? '
		while ...:
			t = input(prompt)
			try: mem[v] = fractions.Fraction(t)
			except ValueError: print(end='Ovo nije racionalni broj ')
			else: break


class Pridruži(AST):
	varijabla: 'IME'
	što: 'broj'
	def izvrši(self, mem, unutar):
		mem[self.varijabla] = self.što.vrijednost(mem, unutar)

class If(AST): 
	uvjet: 'broj'
	onda: 'naredbe*'
	inače: 'naredbe*'
	def izvrši(grananje, mem, unutar):
		b = grananje.uvjet.vrijednost(mem, unutar)
		if b != 0: sljedeći = grananje.onda.izvrši(mem,unutar)
		elif b == 0: sljedeći = grananje.inače.izvrši(mem,unutar)
		else: raise GreškaIzvođenja('Pogreška u if naredbi')



class Print(AST):
	tipvar: 'broj|TEKST|NEWLINE'
	def izvrši(self, mem, unutar):
		if self.tipvar ^ T.NEWLINE: print()
		else:
			t = self.tipvar.vrijednost(mem, unutar)
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
	def vrijednost(self, mem, unutar):
		l, d = self.lijevo.vrijednost(mem, unutar), self.desno.vrijednost(mem, unutar)
		if ((self.manje and l < d) or (self.jednako and l == d) or (self.veće and l > d) or 
			(self.manjej and l <= d) or (self.većej and l >= d) or (self.različito and l != d)): return 1
		else: return 0

class Osnovna(AST):
	operacija: 'T'
	lijevo: 'broj'
	desno: 'broj'
	def vrijednost(self, mem, unutar):
		l, d = self.lijevo.vrijednost(mem, unutar), self.desno.vrijednost(mem, unutar)
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
	def vrijednost(self, mem, unutar):
		o = self.izraz.vrijednost(mem, unutar)
		if self.plusp != nenavedeno:
			return (o+1)
		else:
			return (o-1)

class Povratak(NelokalnaKontrolaToka): """Signal koji šalje naredba vrati."""
		
###################################################################################################
###################################################################################################
###################################################################################################
# TESTNI PRIMJERI 

PrviPrimjer =P('''//rekurzivna funkcija za računanje faktorijela
fakt(n) = {
if n == 0 then 
{
return 1
} 
else 
{
return n*fakt(n-1)} 
endif
}

main() = {
print "unesite broj za koji želite izračunat faktorijel:";
inpt a;
print newline;
return fakt(a);
}''')

#odkomentirat donju liniju za prikaz stabla
#prikaz(PrviPrimjer)
izvrši(PrviPrimjer)


DrugiPrimjer =P('''//rekurzivna funkcija koja računa sumu od 0 do n
sum(n) = {
if n != 0 then 
{
//sve dok je različito od nula pozivamo rekurzivno
return n+sum(n-1)
} 
else 
{
return n} 
endif
}

main() = { 
#u ovom programu računamo sumu brojeva
od 1 do nekog broja a#
print "unesite broj:";
print newline;
inpt a;
print "suma od 1 do a jednaka je: ";
print sum(a);
print newline;
print "sada unesite 3 broja da vidimo je li neki od njih 0: ";
print newline;
inpt x;
inpt y;
inpt z;
res = ? x, y, z;
if res == 0 then{
	print "jedan od brojeva je 0";
}
else {
	print "ni jedan broj nije jednak 0";
}
endif;
print newline;
return 0;
}''')

#odkomentirati donju liniju za prikaz:
#prikaz(DrugiPrimjer)

izvrši(DrugiPrimjer)

TrećiPrimjer =P('''division(a,b) = {
if a < b then{
return a;	
}
else{
return division(a-b,b);
}
endif
}

isPrime(n,i) = {

   if n < 2 then {
        return možda; 
    } 
   
   else {

        if division(n,i) == 0 then {
           return ne;
        }
        else {

             if i*i > n then {
                return da;}
             else {
             	return isPrime(n,i++);
             }
             endif
             
        }
        endif
    }

   endif

}


main() = {
print "unesi broj za provjeru prostosti: ";
inpt t; 
s = isPrime(t,2);
if s == ne then {
	print "to nije prosti broj";
}
else {
	if s == možda then {
	   print "broj nije prirodni";
	}
	else {
       print "broj je prost";
	}
	endif
}
endif;
print newline;
return s;
}''')

#odkomentirati donju liniju za prikaz stabla
#prikaz(TrećiPrimjer)
izvrši(TrećiPrimjer)










