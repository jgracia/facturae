# -*- coding: utf-8 -*-

# @mail ep_niebla@hotmail.com, ep.niebla@gmail.com
# @version 1.0

import os
import math
from fpdf import FPDF

def sprintf(fmt, *args): return fmt % args
def strpos(haystack, needle):
       aux = haystack.find(needle)
       return aux
def strlen(str): return len(str)
def count(l): return len(l)
def strtr(str,from_str,to_str): return str.replace(from_str, to_str)
def substr(s, start, length=-1):
       if length < 0:
               length=len(s)-start
       return s[start:start+length]
def strsetchar(str, pos, val):
    new = list(str)
    new[pos] = val
    return ''.join(new)
class BarCode(FPDF):
    "PDF Generation class"
    T128=[];                                      # Tableau des codes 128
    ABCset = "";                                  # jeu des caractères éligibles au C128
    Aset = "";                                    # Set A du jeu des caractères éligibles
    Bset = "";                                    # Set B du jeu des caractères éligibles
    Cset = "";                                    # Set C du jeu des caractères éligibles
    SetFrom ={"A":'',"B":''};                                      # Convertisseur source des jeux vers le tableau
    SetTo ={"A":'',"B":''};                                        # Convertisseur destination des jeux vers le tableau
    JStart = {"A":103, "B":104, "C":105}; # Caractères de sélection de jeu au début du C128
    JSwap = {"A":101, "B":100, "C":99};   # Caractères de changement de jeu
    def newMargin(self, t=10, r=5, l=10, b=21):
        self.add_page(self.cur_orientation)
        self.set_font('arial','',9);
        self.alias_nb_pages();
        self.set_right_margin(r);
        self.set_left_margin(l);
        self.set_top_margin(t);
        self.set_auto_page_break(True,b);

    def __init__(self, orientation='P',unit='mm',format='A4'):
        super(BarCode,self).__init__(orientation,unit,format)
        self.T128=[];
        self.T128.append([2, 1, 2, 2, 2, 2]); #0 : [ ]     # composition des caractères
        self.T128.append([2, 2, 2, 1, 2, 2]); #1 : [!]
        self.T128.append([2, 2, 2, 2, 2, 1]); #2 : ["]
        self.T128.append([1, 2, 1, 2, 2, 3]); #3 : [#]
        self.T128.append([1, 2, 1, 3, 2, 2]); #4 : []
        self.T128.append([1, 3, 1, 2, 2, 2]); #5 : [%]
        self.T128.append([1, 2, 2, 2, 1, 3]); #6 : [&]
        self.T128.append([1, 2, 2, 3, 1, 2]); #7 : [']
        self.T128.append([1, 3, 2, 2, 1, 2]); #8 : [(]
        self.T128.append([2, 2, 1, 2, 1, 3]); #9 : [)]
        self.T128.append([2, 2, 1, 3, 1, 2]); #10 : [*]
        self.T128.append([2, 3, 1, 2, 1, 2]); #11 : [+]
        self.T128.append([1, 1, 2, 2, 3, 2]); #12 : [,]
        self.T128.append([1, 2, 2, 1, 3, 2]); #13 : [-]
        self.T128.append([1, 2, 2, 2, 3, 1]); #14 : [.]
        self.T128.append([1, 1, 3, 2, 2, 2]); #15 : [/]
        self.T128.append([1, 2, 3, 1, 2, 2]); #16 : [0]
        self.T128.append([1, 2, 3, 2, 2, 1]); #17 : [1]
        self.T128.append([2, 2, 3, 2, 1, 1]); #18 : [2]
        self.T128.append([2, 2, 1, 1, 3, 2]); #19 : [3]
        self.T128.append([2, 2, 1, 2, 3, 1]); #20 : [4]
        self.T128.append([2, 1, 3, 2, 1, 2]); #21 : [5]
        self.T128.append([2, 2, 3, 1, 1, 2]); #22 : [6]
        self.T128.append([3, 1, 2, 1, 3, 1]); #23 : [7]
        self.T128.append([3, 1, 1, 2, 2, 2]); #24 : [8]
        self.T128.append([3, 2, 1, 1, 2, 2]); #25 : [9]
        self.T128.append([3, 2, 1, 2, 2, 1]); #26 : [:]
        self.T128.append([3, 1, 2, 2, 1, 2]); #27 : [;]
        self.T128.append([3, 2, 2, 1, 1, 2]); #28 : [<]
        self.T128.append([3, 2, 2, 2, 1, 1]); #29 : [=]
        self.T128.append([2, 1, 2, 1, 2, 3]); #30 : [>]
        self.T128.append([2, 1, 2, 3, 2, 1]); #31 : [?]
        self.T128.append([2, 3, 2, 1, 2, 1]); #32 : [@]
        self.T128.append([1, 1, 1, 3, 2, 3]); #33 : [A]
        self.T128.append([1, 3, 1, 1, 2, 3]); #34 : [B]
        self.T128.append([1, 3, 1, 3, 2, 1]); #35 : [C]
        self.T128.append([1, 1, 2, 3, 1, 3]); #36 : [D]
        self.T128.append([1, 3, 2, 1, 1, 3]); #37 : [E]
        self.T128.append([1, 3, 2, 3, 1, 1]); #38 : [F]
        self.T128.append([2, 1, 1, 3, 1, 3]); #39 : [G]
        self.T128.append([2, 3, 1, 1, 1, 3]); #40 : [H]
        self.T128.append([2, 3, 1, 3, 1, 1]); #41 : [I]
        self.T128.append([1, 1, 2, 1, 3, 3]); #42 : [J]
        self.T128.append([1, 1, 2, 3, 3, 1]); #43 : [K]
        self.T128.append([1, 3, 2, 1, 3, 1]); #44 : [L]
        self.T128.append([1, 1, 3, 1, 2, 3]); #45 : [M]
        self.T128.append([1, 1, 3, 3, 2, 1]); #46 : [N]
        self.T128.append([1, 3, 3, 1, 2, 1]); #47 : [O]
        self.T128.append([3, 1, 3, 1, 2, 1]); #48 : [P]
        self.T128.append([2, 1, 1, 3, 3, 1]); #49 : [Q]
        self.T128.append([2, 3, 1, 1, 3, 1]); #50 : [R]
        self.T128.append([2, 1, 3, 1, 1, 3]); #51 : [S]
        self.T128.append([2, 1, 3, 3, 1, 1]); #52 : [T]
        self.T128.append([2, 1, 3, 1, 3, 1]); #53 : [U]
        self.T128.append([3, 1, 1, 1, 2, 3]); #54 : [V]
        self.T128.append([3, 1, 1, 3, 2, 1]); #55 : [W]
        self.T128.append([3, 3, 1, 1, 2, 1]); #56 : [X]
        self.T128.append([3, 1, 2, 1, 1, 3]); #57 : [Y]
        self.T128.append([3, 1, 2, 3, 1, 1]); #58 : [Z]
        self.T128.append([3, 3, 2, 1, 1, 1]); #59 : [[]
        self.T128.append([3, 1, 4, 1, 1, 1]); #60 : [\]
        self.T128.append([2, 2, 1, 4, 1, 1]); #61 : []]
        self.T128.append([4, 3, 1, 1, 1, 1]); #62 : [^]
        self.T128.append([1, 1, 1, 2, 2, 4]); #63 : [_]
        self.T128.append([1, 1, 1, 4, 2, 2]); #64 : [`]
        self.T128.append([1, 2, 1, 1, 2, 4]); #65 : [a]
        self.T128.append([1, 2, 1, 4, 2, 1]); #66 : [b]
        self.T128.append([1, 4, 1, 1, 2, 2]); #67 : [c]
        self.T128.append([1, 4, 1, 2, 2, 1]); #68 : [d]
        self.T128.append([1, 1, 2, 2, 1, 4]); #69 : [e]
        self.T128.append([1, 1, 2, 4, 1, 2]); #70 : [f]
        self.T128.append([1, 2, 2, 1, 1, 4]); #71 : [g]
        self.T128.append([1, 2, 2, 4, 1, 1]); #72 : [h]
        self.T128.append([1, 4, 2, 1, 1, 2]); #73 : [i]
        self.T128.append([1, 4, 2, 2, 1, 1]); #74 : [j]
        self.T128.append([2, 4, 1, 2, 1, 1]); #75 : [k]
        self.T128.append([2, 2, 1, 1, 1, 4]); #76 : [l]
        self.T128.append([4, 1, 3, 1, 1, 1]); #77 : [m]
        self.T128.append([2, 4, 1, 1, 1, 2]); #78 : [n]
        self.T128.append([1, 3, 4, 1, 1, 1]); #79 : [o]
        self.T128.append([1, 1, 1, 2, 4, 2]); #80 : [p]
        self.T128.append([1, 2, 1, 1, 4, 2]); #81 : [q]
        self.T128.append([1, 2, 1, 2, 4, 1]); #82 : [r]
        self.T128.append([1, 1, 4, 2, 1, 2]); #83 : [s]
        self.T128.append([1, 2, 4, 1, 1, 2]); #84 : [t]
        self.T128.append([1, 2, 4, 2, 1, 1]); #85 : [u]
        self.T128.append([4, 1, 1, 2, 1, 2]); #86 : [v]
        self.T128.append([4, 2, 1, 1, 1, 2]); #87 : [w]
        self.T128.append([4, 2, 1, 2, 1, 1]); #88 : [x]
        self.T128.append([2, 1, 2, 1, 4, 1]); #89 : [y]
        self.T128.append([2, 1, 4, 1, 2, 1]); #90 : [z]
        self.T128.append([4, 1, 2, 1, 2, 1]); #91 : [{]
        self.T128.append([1, 1, 1, 1, 4, 3]); #92 : [|]
        self.T128.append([1, 1, 1, 3, 4, 1]); #93 : [}]
        self.T128.append([1, 3, 1, 1, 4, 1]); #94 : [~]
        self.T128.append([1, 1, 4, 1, 1, 3]); #95 : [DEL]
        self.T128.append([1, 1, 4, 3, 1, 1]); #96 : [FNC3]
        self.T128.append([4, 1, 1, 1, 1, 3]); #97 : [FNC2]
        self.T128.append([4, 1, 1, 3, 1, 1]); #98 : [SHIFT]
        self.T128.append([1, 1, 3, 1, 4, 1]); #99 : [Cswap]
        self.T128.append([1, 1, 4, 1, 3, 1]); #100 : [Bswap]
        self.T128.append([3, 1, 1, 1, 4, 1]); #101 : [Aswap]
        self.T128.append([4, 1, 1, 1, 3, 1]); #102 : [FNC1]
        self.T128.append([2, 1, 1, 4, 1, 2]); #103 : [Astart]
        self.T128.append([2, 1, 1, 2, 1, 4]); #104 : [Bstart]
        self.T128.append([2, 1, 1, 2, 3, 2]); #105 : [Cstart]
        self.T128.append([2, 3, 3, 1, 1, 1]); #106 : [STOP]
        self.T128.append([2, 1]);             #107 : [END BAR]

        for i in range(32,(95+1)):  # jeux de caractères
            self.ABCset += chr(i);

        self.Aset = self.ABCset;
        self.Bset = self.ABCset;

        for i in range(0,(31+1)):
            self.ABCset += chr(i);
            self.Aset += chr(i);

        for i in range(96,(127+1)):
            self.ABCset += chr(i);
            self.Bset += chr(i);

        for i in range(200,(210+1)):  # controle 128
            self.ABCset += chr(i);
            self.Aset += chr(i);
            self.Bset += chr(i);

        self.Cset="0123456789"+chr(206);

        for i in range(0,96): # convertisseurs des jeux A & B
            self.SetFrom["A"] += chr(i);
            self.SetFrom["B"] += chr(i + 32);
            if i < 32:
                self.SetTo["A"] += chr( i+64 );
            else:
                self.SetTo["A"] += chr( i-32 );
            self.SetTo["B"] += chr(i);

        for i in range(96,107): # contrôle des jeux A & B
            self.SetFrom["A"] += chr(i + 104);
            self.SetFrom["B"] += chr(i + 104);
            self.SetTo["A"] += chr(i);
            self.SetTo["B"] += chr(i);



    def Code128(self, x, y, code, w, h) :
        Aguid = "";                                                                      # Création des guides de choix ABC
        Bguid = "";
        Cguid = "";

        for i in range(0,strlen(code)):
            needle = substr(code,i,1);

            Aguid += ("N" if strpos(self.Aset,needle)==-1 else "O");
            Bguid += ("N" if strpos(self.Bset,needle)==-1 else "O");
            Cguid += ("N" if strpos(self.Cset,needle)==-1 else "O");


        SminiC = "OOOO";
        IminiC = 4;

        crypt = "";
        while code > "": # BOUCLE PRINCIPALE DE CODAGE
			i = strpos(Cguid,SminiC);                                                # forçage du jeu C, si possible

			if i!=-1:
				Aguid = strsetchar(Aguid, i, "N")
				Bguid = strsetchar(Bguid, i, "N")


			if substr(Cguid,0,IminiC) == SminiC:                                  # jeu C

				crypt +=  chr( self.JSwap["C"] if (crypt > "") else self.JStart["C"]);  # début Cstart, sinon Cswap

				made = strpos(Cguid,"N");                                             # étendu du set C
				if made == -1:
					made = strlen(Cguid);


				if math.fmod(made,2)==1:
					made=made-1;

				for i in range(0,made,2):
					crypt += chr(int(substr(code,i,2)));                          # conversion 2 par 2

				jeu = "C";

			else:
				madeA = strpos(Aguid,"N");                                            # étendu du set A
				if madeA == -1:
					madeA = strlen(Aguid);

				madeB = strpos(Bguid,"N");                                            # étendu du set B
				if madeB == -1:
					madeB = strlen(Bguid);

				made = ( madeB if (madeA < madeB) else madeA );                         # étendu traitée
				jeu = ( "B" if (madeA < madeB) else "A" );                                # Jeu en cours

				crypt += chr( self.JSwap[jeu] if (crypt > "") else self.JStart[jeu]); # début start, sinon swap

				crypt += strtr(substr(code, 0,made), self.SetFrom[jeu], self.SetTo[jeu]); # conversion selon jeu


			code = substr(code,made);                                           # raccourcir légende et guides de la zone traitée
			Aguid = substr(Aguid,made);
			Bguid = substr(Bguid,made);
			Cguid = substr(Cguid,made);

        check = ord(crypt[0]);

        for i in range(0,strlen(crypt)):
			check += (ord(crypt[i]) * i);

        check %= 103;

        crypt += chr(check) + chr(106) + chr(107);                               # Chaine cryptée complète

        i = (strlen(crypt) * 11) - 8;                                            # calcul de la largeur du module
        modul = float(w)/int(i);
        #print(str( float(82.0/int(146)) ) )

        for i in range(0,strlen(crypt)):                                   # BOUCLE D'IMPRESSION

			c = self.T128[ord(crypt[i])];

			for j in range(0,count(c),2):
				self.rect(x,y,c[j]*modul,h,"F");

				x += ( (0 if ((j+1)>=count(c)) else c[(j+1)]) +c[j])*modul;


    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def RoundedRect(self, x, y, w, h, r, corners = '1234', style = ''):
        k = self.k;
        hp = self.h;
        if style=='F':
            op='f';
        else:
            if style=='FD' or style=='DF':
                op='B';
            else:
                op='S';
        MyArc = 4/3 * (math.sqrt(2) - 1);
        self._out(sprintf('%.2F %.2F m',(x+r)*k,(hp-y)*k ));

        xc = x+w-r;
        yc = y+r;
        self._out(sprintf('%.2F %.2F l', xc*k,(hp-y)*k ));
        if strpos(corners, '2')==-1:
            self._out(sprintf('%.2F %.2F l', (x+w)*k,(hp-y)*k ));
        else:
            self._Arc(xc + r*MyArc, yc - r, xc + r, yc - r*MyArc, xc + r, yc);

        xc = x+w-r;
        yc = y+h-r;
        self._out(sprintf('%.2F %.2F l',(x+w)*k,(hp-yc)*k));
        if strpos(corners, '3')==-1:
            self._out(sprintf('%.2F %.2F l',(x+w)*k,(hp-(y+h))*k));
        else:
            self._Arc(xc + r, yc + r*MyArc, xc + r*MyArc, yc + r, xc, yc + r);

        xc = x+r;
        yc = y+h-r;
        self._out(sprintf('%.2F %.2F l',xc*k,(hp-(y+h))*k));
        if strpos(corners, '4')==-1:
            self._out(sprintf('%.2F %.2F l',(x)*k,(hp-(y+h))*k));
        else:
            self._Arc(xc - r*MyArc, yc + r, xc - r, yc + r*MyArc, xc - r, yc);

        xc = x+r ;
        yc = y+r;
        self._out(sprintf('%.2F %.2F l',(x)*k,(hp-yc)*k ));
        if strpos(corners, '1')==-1:
            self._out(sprintf('%.2F %.2F l',(x)*k,(hp-y)*k ));
            self._out(sprintf('%.2F %.2F l',(x+r)*k,(hp-y)*k ));
        else:
            self._Arc(xc - r, yc - r*MyArc, xc - r*MyArc, yc - r, xc, yc - r);
        self._out(op);


    def _Arc(self, x1, y1, x2, y2, x3, y3):
        h = self.h;
        self._out(sprintf('%.2F %.2F %.2F %.2F %.2F %.2F c ', x1*self.k, (h-y1)*self.k, x2*self.k, (h-y2)*self.k, x3*self.k, (h-y3)*self.k));
