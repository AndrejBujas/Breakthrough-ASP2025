import pygame
import time
from typing import List,Tuple, Dict
from dataclasses import dataclass
from math import inf
import pygame

racunanja = 0
VELICINA = 7
Potez = Tuple[int,int,int,int]

transposition_table: Dict[int, Tuple[int, int]] = {}



class Square:
    def __init__(self, x, y, width, height,):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.abs_x = x * width
        self.abs_y = y * height
        self.abs_pos = (self.abs_x, self.abs_y)
        self.pos = (x, y)
        self.color = "white" if (x+y)%2 == 0 else "gray"
        self.draw_color = (220, 208, 194) if self.color == 'light' else (53, 53, 53)
        self.highlight_color = (100, 249, 83) if self.color == 'light' else (0, 228, 10)
        self.border_color = (0, 120, 255)
        self.highlight_figura = False
        self.highlight = False
        self.figura = None


        self.rect = pygame.Rect(
            self.abs_x,
            self.abs_y,
            self.width,
            self.height
        )


    def draw(self,display):

        if self.highlight:
            pygame.draw.rect(display, self.highlight_color, self.rect)
        elif self.highlight_figura:
            pygame.draw.rect(display, self.border_color, self.rect, 4)
        else:
            pygame.draw.rect(display, self.color, self.rect)

        if self.figura == "B":
            pygame.draw.circle(display, (0,0,0), self.rect.center, self.width /3)
        if self.figura == "W":
            pygame.draw.circle(display, (255,255,255), self.rect.center, self.width /3)
            pygame.draw.circle(display, (155,155,155), self.rect.center, self.width /3, 3)

class Board:
    def __init__(self, width, height,velicina):
        self.width = width
        self.height = height
        self.tile_width = width // velicina
        self.tile_height = height // velicina
        self.selected_piece = None
        self.velicina = velicina
        self.polja = self.podesi_tablu()


    def podesi_tablu(self):
        tabla = []
        for y in range(self.velicina):
            red = []
            for x in range(self.velicina):
                kvadrat = Square(x, y, 80, 80)
                if y < 2:
                    kvadrat.figura = "B"
                if y > 5:
                    kvadrat.figura = "W"
                red.append(kvadrat)
            tabla.append(red)
        return tabla

    def polje_na_poziciji(self, mouse_pos):
        for red in self.polja:
            for kvadrat in red:
                if kvadrat.rect.collidepoint(mouse_pos):
                    return kvadrat

        return None


    def selektuj(self, mouse_pos,potezi):
        kliknuti = self.polje_na_poziciji(mouse_pos)

        if kliknuti == self.selected_piece:
            kliknuti.highlight_figura = False
            self.selected_piece = None
            for red in self.polja:
                for kvadrat in red:
                    kvadrat.highlight = False
            return

        for red in self.polja:
            for kvadrat in red:
                kvadrat.highlight_figura = False
                kvadrat.highlight = False

        if kliknuti and kliknuti.figura == "W":
            xk = kliknuti.x
            yk = kliknuti.y


            validan = False
            for potez in potezi:
                (y,x,ny,nx) = potez
                if x == xk and y == yk and not validan:
                    kliknuti.highlight_figura = True
                    self.selected_piece = kliknuti
                if x == xk and y == yk:
                    for red in self.polja:
                        for kvadrat in red:
                            if kvadrat.x == nx and kvadrat.y == ny:
                                kvadrat.highlight = True


        else:
            self.selected_piece = None

    def generisi_potez(self, selected_piece, kliknuto, potezi):
        xs = selected_piece.x
        ys = selected_piece.y
        xk = kliknuto.x
        yk = kliknuto.y
        for potez in potezi:
            (y,x,ny,nx) = potez
            if x == xs and y == ys and xk == nx and yk == ny:
                return potez

    def update_from_state(self, state):
        for y in range(self.velicina):
            for x in range(self.velicina):
                figura = state.board[y][x]
                self.polja[y][x].figura = figura

            # Resetuj selekciju i highlight
        for red in self.polja:
            for kvadrat in red:
                kvadrat.highlight = False
                kvadrat.highlight_figura = False
                kvadrat.selected = False



    def draw(self, display):
        for red in self.polja:
            for kvadrat in red:
                kvadrat.draw(display)


@dataclass
class GameState:
    board: List[List[str]]
    turn: str
    last_move: Potez | None = None

    def clone(self):
        return GameState([row[:] for row in self.board], self.turn, self.last_move)

    def kraj(self):
        for i in range(VELICINA):
            if self.board[0][i] == 'W':
                return "W"
            if self.board[VELICINA-1][i] == 'B':
                return "B"

        ima_belih = any("W" in row for row in self.board)
        ima_crnih = any("B" in row for row in self.board)
        if not ima_belih:
            return "B"
        if not ima_crnih:
            return "W"


def hash_state(state: GameState) -> int:
    return hash((''.join(''.join(row) for row in state.board), state.turn))

def napravi_tablu():
    t = [["."]*VELICINA for x in range(VELICINA)]
    for i in range(2):
        for j in range(VELICINA):
            t[i][j] = "B"
    for i in range(VELICINA-2,VELICINA):
        for j in range(VELICINA):
            t[i][j] = "W"

    return t

def print_tabla(state: GameState):
    print('   ' + ' '.join(str(c) for c in range(VELICINA)))
    for r in range(VELICINA):
        print(f'{r}  ' + ' '.join(state.board[r]))
    print(f"Na redu: {state.turn}")

def primeni_potez(state: GameState, mv: tuple):
    ns = state.clone()
    r0, k0, r1, k1 = mv
    ns.board[r1][k1] = ns.board[r0][k0]
    ns.board[r0][k0] = "."
    ns.turn = "B" if ns.turn == "W" else "W"
    return ns


def potezi(state: GameState):
    potezi = []
    smer = -1 if state.turn == "W" else 1
    for r in range(VELICINA):
        for k in range(VELICINA):
            if state.board[r][k] != state.turn:
                continue

            nr,nk = r + smer, k
            if  0 <= nr < VELICINA and  0 <= nk < VELICINA and state.board[nr][nk] == ".":
                potezi.append((r,k,nr,nk))

            nr,nk = r + smer, k - 1
            if  0 <= nr < VELICINA and  0 <= nk < VELICINA and state.board[nr][nk] != state.turn :
                potezi.append((r,k,nr,nk))
            nr,nk = r + smer, k + 1
            if  0 <= nr < VELICINA and  0 <= nk < VELICINA and state.board[nr][nk] != state.turn:
                potezi.append((r,k,nr,nk))
    return potezi



# def heuristika(state: GameState) -> int:
#     board = state.board
#     igrac = "B"
#     protivnik = "W"
#
#     score = 0
#
#     #Materijal
#     crni = sum(row.count(igrac) for row in board)
#     beli = sum(row.count(protivnik) for row in board)
#     score += (crni - beli) * 100
#
#     #Mobilnost
#     moje_poteza = len(potezi(state))
#     score += moje_poteza * 5
#
#     # Progresija ka cilju
#     for r in range(8):
#         for c in range(8):
#             if board[r][c] == igrac:
#                 score += (7 - r) * 10
#             elif board[r][c] == protivnik:
#                 score -= r * 10
#
#     #Sides proximity
#     for r in range(8):
#         for c in range(8):
#             if board[r][c] == igrac:
#                 dist_side = min(c, 7 - c)
#                 score += (3 - dist_side) * 15
#
#     #Centre proximity
#     for r in range(8):
#         for c in range(8):
#             if board[r][c] == igrac:
#                 dist_center = abs(c - 3.5)
#                 score -= int(dist_center) * 2
#
#     return score

def heuristika(state: GameState) -> int:
    board = state.board

    crni = beli = 0
    score = 0

    for r in range(VELICINA):
        for c in range(VELICINA):
            fig = board[r][c]
            if fig == "B":
                crni += 1
                score += (7 - r) * 10               # progresija
                dist_side = min(c, 7 - c)
                score += (3 - dist_side) * 15       # stranično
                dist_center = abs(c - 3.5)
                score -= int(dist_center) * 2       # centar
            elif fig == "W":
                beli += 1
                score -= r * 10
                dist_side = min(c, 7 - c)
                score -= (3 - dist_side) * 15
                dist_center = abs(c - 3.5)
                score += int(dist_center) * 2

    # materijal
    score += (crni - beli) * 100

    # mobilnost
    score += (crni - beli) * 3

    return score

def minimax(state: GameState, depth: int, alpha: int, beta: int,maximizing: bool):
    hash = hash_state(state)
    if hash in transposition_table:
        dubina, eval = transposition_table[hash]
        if dubina >= depth:
            return eval

    if depth == 0 or state.kraj() is not None:
        eval_v = heuristika(state)
        transposition_table[hash] = (depth, eval_v)
        return eval_v

    if maximizing == True:
        maxEval = -float("inf")


        for potez in potezi(state):
            ns = primeni_potez(state, potez)
            eval = minimax(ns, depth - 1, alpha, beta,False)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        transposition_table[hash] = (depth, maxEval)
        return maxEval
    else:
        minEval = float("inf")


        for potez in potezi(state):
            ns = primeni_potez(state, potez)
            eval = minimax(ns, depth - 1, alpha, beta, True)
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        transposition_table[hash] = (depth, minEval)
        return minEval

def naj_potez(state: GameState,dubina):
    start = time.time()
    najpt = None
    naj_vrednost = -float("inf")

    for pt in potezi(state):
        ns = primeni_potez(state, pt)
        vrednost = minimax(ns, dubina, -float("inf"), float("inf"), False)

        if vrednost > naj_vrednost:
            naj_vrednost = vrednost
            najpt = pt
    end = time.time()
    print(f"AI potez gotov za {end - start:.2f} sekundi (dubina={dubina})")
    return najpt



def pokreni_igru():


    # state = GameState(napravi_tablu(),'W')
    # print(potezi(state))
    # while True:
    #
    #     if state.turn == "W":
    #         print_tabla(state)
    #         pt = potezi(state)
    #         print(pt)
    #         izbor = int(input("Izaberi potez"))
    #         state = primeni_potez(state, pt[izbor])
    #
    #     else:
    #         pt = naj_potez(state, 2)
    #         print(pt)
    #         state = primeni_potez(state, pt)


    pygame.init()
    WIDTH, HEIGHT = 640, 640
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Inicijalno stanje
    state = GameState(napravi_tablu(), 'W')
    tabla = Board(WIDTH, HEIGHT, VELICINA)
    tabla.update_from_state(state)



    run = True
    while run:
        clock.tick(10)
        kraj = state.kraj()

        if kraj == "W":
            run = False
        if kraj == "B":
            run = False


        if state.turn == "B":
            ai_potez = naj_potez(state, 4)
            state = primeni_potez(state, ai_potez)
            tabla.update_from_state(state)



        pt = potezi(state)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN and state.turn == "W":
                kliknuto = tabla.polje_na_poziciji(pygame.mouse.get_pos())

                if kliknuto and kliknuto.highlight:
                    potez = tabla.generisi_potez(tabla.selected_piece, kliknuto, pt)
                    state = primeni_potez(state, potez)
                    tabla.update_from_state(state)
                else:
                    tabla.selektuj(pygame.mouse.get_pos(),pt)

        # Crtanje
        screen.fill((0, 0, 0))
        tabla.draw(screen)
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    pokreni_igru()