# Domaća zadaća
## Napravili: Ivona Čižić, Barbara Posavec, Luka Jandrijević

Domaća zadaća iz kolegija Interpretacija programa: programski jezik "Snail".


Snail se sastoji od 4 vrste izjava:

- assign
- print
- if
- (while) - ne treba implementirati - koriste se rekurzije

Osnovna komponenta u svakoj izjavi je "expression" koji se sastoji od: 

- identifikator 
- vrijednost identifikatora je zadnja pridružena vrijednost tom identifikatoru\
- identifikator koji nema pridruženu vrijednost se ne smije koristit u "expression-u"\
- integer
-zagrade - ()
- aritmetičke operacije: + - * /
- operatori usporedbe: < &ensp; > &ensp; <= &ensp; >= &ensp; == &ensp; != (output je 1 za istinu i 0 za laž za sve navedene)

npr: 10 + 20 * (10 < 3) = 10 + 20 * 0 = 10 jer 10 < 3 = 0 jer je laž

__________________________________________________________________
"assign" -> oblika:
        
        identifier = expression;
		
		
	npr:
		var1 = 20 - 3*2;

__________________________________________________________________
"print" -> oblika:

		print "string"; 
		print newline;
		print expression;  (ispisuje vrijednost izraza)

    
    npr:
    print "The value of 10*5 is ";
    print 10*5;

ispis: The value of 10*5 is 50
__________________________________________________________________
    if expression then
	    statement
	    statement
	    ...
    endif

if expression then
	statement
	...
else
	statement
	...
endif


Značenje isto kao u C-u i drugim programskim jezicima
__________________________________________________________________

Snail program je u formi:

    izjava
    izjava
    ...
    izjava


Također imamo jednolinijske komentare označene sa "//" kao i u C-u
