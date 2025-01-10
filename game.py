import pgzrun

# Variáveis Globais
game_state = "menu"  # Estados possíveis: menu, playing
music_on = True
camera_x = 0  # Deslocamento horizontal da câmera
game_over_message = ""

WIDTH = 800
HEIGHT = 600
TITLE = "Platformer Game"

music.play("cruising")  # Toca a música ao iniciar o jogo

menu_start_button = Actor("losango_verde", (WIDTH // 2, HEIGHT // 2 - 20))
menu_start_button.scale = 0.5  # Reduz o tamanho para 50%

menu_music_button = Actor("losango_azul", (WIDTH // 2, HEIGHT // 2 + 65))
menu_music_button.scale = 0.5

menu_exit_button = Actor("losango_vermelho", (WIDTH // 2, HEIGHT // 2 + 150))
menu_exit_button.scale = 0.1

rocket_final = Actor(
    "foguete_final",
    (WIDTH //
     2,
     HEIGHT +
     200))  # Começa fora da tela
rocket_active = False  # Indica se o foguete deve ser mostrado


# Classe Hero para gerenciar o personagem principal
class Hero:
    def __init__(self, x, y):
        self.initial_x = x
        self.initial_y = y
        self.actor = Actor("heroi_idle", (x, y))  # Sprite inicial
        self.vx = 0
        self.vy = 0
        self.on_ground = True
        self.animation_timer = 0
        self.health = 6  # Vida que inicio
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.visible = True
        self.facing_right = False  # Indica se está olhando para a direita

    def take_damage(self):
        if not self.invulnerable:  # Só toma dano se não estiver invulnerável
            self.health -= 1
            sounds.damage.play()  # Toca o som de dano
            if self.health <= 0:
                global game_state, game_over_message
                game_state = "game_over"
                game_over_message = "Game Over! Press ESC to return to menu"
                self.reset_position()  # Reseta posição e câmera
                self.health = 6  # Reiniciar vida
            else:
                self.invulnerable = True  # Ativar invulnerabilidade
                self.invulnerable_timer = 150  # 2.5 segundos (150 frames a 60 FPS)



    def handle_invulnerability(self):
        if self.invulnerable:
            self.invulnerable_timer -= 1
            self.visible = self.invulnerable_timer % 10 < 5
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
                self.visible = True

    def draw(self):
        if self.visible:
            self.actor.draw()


    def move(self):
        # Aplicar gravidade
        self.vy += 0.5  # Aceleração da gravidade

        # Atualizar posição com velocidades
        self.actor.x += self.vx
        self.actor.y += self.vy

        # Limitar dentro da tela horizontalmente
        self.actor.x = max(
            0, min(
                self.actor.x, len(
                    level_map[0]) * 18 - self.actor.width))

        # Assume que não está no ar
        self.on_ground = False

        for platform in platforms:
            for block in platform:
                if block.image in [
                    "invisible_barrier",
                    "flag",
                        "flag1"]:  # Ignorar barreiras invisíveis e bandeiras
                    continue

                if self.actor.colliderect(block):
                    if block.image == "spike":  # Espinhos causam dano
                        self.take_damage()
                    elif block.image == "rocket":  # Foguete indica vitória
                        global game_state, game_over_message, rocket_active
                        game_state = "game_over"
                        game_over_message = "You Win! Press ESC to return to menu"
                        music.stop()  # Parar a música atual

                        # Ativar o foguete e tocar a música de vitória
                        rocket_active = True
                        sounds.victory.play()
                        sounds.propulsor.play()
                        # Agendar o som do propulsor após a música de vitória terminar
                       # clock.schedule(lambda: sounds.propulsor.play(), 4.0)
                    elif self.vy > 0 and self.actor.bottom <= block.bottom:
                        self.actor.bottom = block.top
                        self.on_ground = True  # Está no chão
                        self.vy = 0
                    elif block.image not in ["spike", None, "rocket"]:
                        if self.vx > 0:  # Indo para a direita
                            self.actor.right = block.left
                            self.vx = 0
                        elif self.vx < 0:  # Indo para a esquerda
                            self.actor.left = block.right
                            self.vx = 0

    def update_sprite(self):
        # Incrementar o temporizador de animação
        self.animation_timer += 1

        # Controle de sprites de idle (parado)
        if self.vx == 0:  # Sem movimento
            if self.animation_timer % 10 == 0:  # Alternar sprite a cada 10 frames
                if self.facing_right:  # Idle olhando para a direita
                    if self.actor.image == "heroi_idle_direita":
                        self.actor.image = "heroi_idle1_direita"
                    elif self.actor.image == "heroi_idle1_direita":
                        self.actor.image = "heroi_idle2_direita"
                    else:
                        self.actor.image = "heroi_idle_direita"
                else:  # Idle olhando para a esquerda
                    if self.actor.image == "heroi_idle":
                        self.actor.image = "heroi_idle1"
                    elif self.actor.image == "heroi_idle1":
                        self.actor.image = "heroi_idle2"
                    else:
                        self.actor.image = "heroi_idle"

        # Controle de sprites de movimento (caminhada)
        elif self.vx != 0:  # Movimento horizontal
            if self.vx > 0:  # Movendo para a direita
                self.facing_right = True  # Atualiza a direção
                if self.animation_timer % 10 == 0:  # Alternar sprite a cada 10 frames
                    if self.actor.image == "heroi_idle_direita":
                        self.actor.image = "heroi_walk_direita"
                    elif self.actor.image == "heroi_walk_direita":
                        self.actor.image = "heroi_idle1_direita"
                    elif self.actor.image == "heroi_idle1_direita":
                        self.actor.image = "heroi_walk1_direita"
                    elif self.actor.image == "heroi_walk1_direita":
                        self.actor.image = "heroi_idle2_direita"
                    else:
                        self.actor.image = "heroi_idle_direita"
            else:  # Movendo para a esquerda
                self.facing_right = False  # Atualiza a direção
                if self.animation_timer % 10 == 0:  # Alternar sprite a cada 10 frames
                    if self.actor.image == "heroi_idle":
                        self.actor.image = "heroi_walk"
                    elif self.actor.image == "heroi_walk":
                        self.actor.image = "heroi_idle1"
                    elif self.actor.image == "heroi_idle1":
                        self.actor.image = "heroi_walk1"
                    elif self.actor.image == "heroi_walk1":
                        self.actor.image = "heroi_idle2"
                    else:
                        self.actor.image = "heroi_idle"

    def reset_position(self):
        self.actor.x = self.initial_x
        self.actor.y = self.initial_y
        self.vx = 0
        self.vy = 0
        global camera_x
        camera_x = max(0, min(self.actor.x - WIDTH // 2,
                       len(level_map[0]) * 18 - WIDTH))

# Classe Enemy para gerenciar inimigos


class Enemy:
    def __init__(self, x, y):
        self.actor = Actor("enemy_idle", (x, y))  # Sprite inicial
        self.vx = 2  # Velocidade de patrulha
        self.is_attacking = False  # Define se está atacando
        self.animation_timer = 0  # Timer para animações

    def draw(self):
        # Ajustar posição com a câmera antes de desenhar
        self.actor.pos = (self.actor.x - camera_x, self.actor.y)
        self.actor.draw()

    def patrol(self, platforms):
        # Move o inimigo na direção atual
        self.actor.x += self.vx

        # Verifica se o inimigo encontrou o bloco "!" na matriz
        for platform in platforms:
            for block in platform:
                if block.colliderect(
                        self.actor) and block.image == "invisible_barrier":  # Nome do sprite do "!"
                    self.vx = -self.vx  # Inverte a direção
                    break

    def detect_player(self, player):
        # Detectar jogador em um raio
        distance = abs(self.actor.x - player.actor.x)
        if distance < 200:  # Raio de alcance (200 pixels)
            self.is_attacking = True
            self.actor.image = "enemy_attack"  # Muda sprite para ataque
        else:
            self.is_attacking = False
            self.actor.image = "enemy_idle"  # Volta para idle

    def shoot(self, projectiles, player):
        if self.is_attacking:
            self.animation_timer += 1
            if self.animation_timer % 50 == 0:  # Atira a cada 50 frames
                direction = 1 if player.actor.x > self.actor.x else -1
                projectiles.append(
                    Projectile(
                        self.actor.x,
                        self.actor.y,
                        direction))
                sounds.shoot.play()  # Toca o som do tiro


# Classe Projectile para gerenciar projéteis
class Projectile:
    def __init__(self, x, y, direction):
        self.actor = Actor("bullet", (x, y))
        self.vx = 5 * direction  # Velocidade do projétil

    def draw(self):
        self.actor.draw()

    def move(self):
        self.actor.x += self.vx


# Inicialização do herói
hero = Hero(WIDTH // 2, HEIGHT - 100)

# Lista de inimigos e projéteis
enemies = []  # Lista de inimigos será carregada dinamicamente
projectiles = []  # Lista de projéteis

# Representação do mapa do nível


level_map = [
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
    "!@@E@@@@!!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
    "PPPPPPPPPP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PPPPPPPP@@@@@@@@@@@@@@@@@@@@@@!@E@@@@!@@@@@@@@@@@@@@@@@@@@PPPPP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PPPPPP@@@@@@@@@@@PPPPPPPP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PPPPPPPPP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PPPPPPPP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PPPPPPPP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PPPPPPP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PPPPPPPPPP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PPP@@@@PP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@V@@@@",
    "@@@@@@@@@@@@@@@@@@@R@@@@@@@@@@@@@@@@@@@@@@@@@@@@@!@@@@@@@@@@@@E!@@@@@@@@@@@@@@@@@@@@@@@@@@@@!@@E@@@@@!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@!E@@@@@@@E!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@PPP@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@H@@@@@@@",
    "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGKKKKGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGKKKKGGGGGGGGGGGGGGGGGGGGGGGGKKGGGGKKGGGGGGGKKKKKKKGGGGGGGGGGGGGGGGGGGGGGGGGG",
    "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTGGGGTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTGGGGTTTTTTTTTTTTTTTTTTTTTTTTGGTTTTGGTTTTTTTGGGGGGGTTTTTTTTTTTTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
    "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",

]


# Mapeamento de sprites para cada caractere
block_types = {
    "T": "terra",       # Terra
    "G": "grama",       # Grama
    "P": "plataforma",  # Plataforma
    "@": None,           # Espaço vazio (sem sprite)
    "E": None,            # Indica spawn de inimigo
    "!": "invisible_barrier",  # Sprite invisível
    "K": "spike",        # Espinho (novo caractere)
    "V": "rocket",  # Foguete do final
    "H": "flag"       # Bandeira de chegada

}


# Função para carregar o mapa e criar as plataformas e inimigos
def load_map():
    platforms = []
    map_height = len(level_map) * 18  # Altura total do mapa em pixels
    y_offset = HEIGHT - map_height    # Ajuste para alinhar ao fundo da tela

    for y, row in enumerate(level_map):
        platform_row = []
        for x, cell in enumerate(row):
            if cell == "R":  # Indicar respawn
                hero.initial_x = x * 18
                hero.initial_y = y * 18 + y_offset
            # Verifica se o caractere tem um sprite associado
            elif cell in block_types and block_types[cell]:
                actor = Actor(block_types[cell], (x * 18, y * 18 + y_offset))
                # Se for bandeira, começar com o sprite inicial
                if block_types[cell] == "flag":
                    actor.image = "flag"
                platform_row.append(actor)
            elif cell == "E":
                enemy_x = x * 18
                enemy_y = y * 18 + y_offset
                enemies.append(Enemy(enemy_x, enemy_y))
        if platform_row:
            platforms.append(platform_row)
    return platforms


# Carregar o mapa
platforms = load_map()


def draw():
    screen.clear()
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "game_over":
        screen.draw.text(
            game_over_message,
            center=(WIDTH // 2, HEIGHT // 2),
            fontsize=50,
            color="red"
        )

    # Desenhar o foguete quando ativo
    if rocket_active:
        rocket_final.draw()


def draw_menu():
    screen.draw.text(
        "Platformer Game",
        center=(
            WIDTH // 2,
            HEIGHT // 4),
        fontsize=50,
        color="white")

    # Botão "Start Game"
    menu_start_button.draw()
    screen.draw.text(
        "Play",
        center=menu_start_button.center,
        fontsize=30,
        color="black")

    # Botão "Toggle Music"
    menu_music_button.draw()
    screen.draw.text(
        "Toggle Music",
        center=menu_music_button.center,
        fontsize=30,
        color="black")

    # Botão "Exit"
    menu_exit_button.draw()
    screen.draw.text(
        "Exit",
        center=menu_exit_button.center,
        fontsize=30,
        color="black")


def on_mouse_down(pos):
    global game_state, music_on

    if game_state == "menu":
        if menu_start_button.collidepoint(pos):
            game_state = "playing"
            if music_on:
                music.play("cruising")

        elif menu_music_button.collidepoint(pos):
            music_on = not music_on
            if music_on:
                menu_music_button.image = "losango_azul"
                music.play("cruising")
            else:
                menu_music_button.image = "losango_cinza"
                music.stop()

        elif menu_exit_button.collidepoint(pos):
            exit()


def draw_game():
    # Desenhar o background estático
    screen.blit("background", (0, 0))

    # Desenhar plataformas com base na posição da câmera
    for platform in platforms:
        for block in platform:
            # Ajustar posição com a câmera
            block.pos = (block.x - camera_x, block.y)
            block.draw()

    # Desenhar o herói
    hero.actor.pos = (hero.actor.x - camera_x, hero.actor.y)
    hero.draw()

    # Desenhar inimigos
    for enemy in enemies:
        enemy.draw()

    # Desenhar projéteis
    for projectile in projectiles:
        projectile.draw()

    # Desenhar corações no canto superior esquerdo
    for i in range(hero.health // 2):
        screen.blit("heart_full", (10 + i * 40, 10))
    if hero.health % 2 == 1:  # Meio coração
        screen.blit("heart_half", (10 + (hero.health // 2) * 40, 10))


def reset_game():
    global hero, enemies, projectiles, platforms, camera_x, game_state, music_on

    # Reiniciar estado global
    game_state = "menu"
    camera_x = 0
    music_on = True

    # Recriar herói na posição inicial
    hero = Hero(WIDTH // 2, HEIGHT - 100)

    # Recarregar mapa e plataformas
    platforms = load_map()

    # Recriar listas de inimigos e projéteis
    enemies = []
    projectiles = []
    for y, row in enumerate(level_map):
        for x, cell in enumerate(row):
            if cell == "E":
                enemy_x = x * 18
                enemy_y = HEIGHT - len(level_map) * 18 + y * 18
                enemies.append(Enemy(enemy_x, enemy_y))


def on_key_down(key):
    global game_state, music_on

    # Verifica se está no estado "game_over" e o jogador deseja voltar ao menu
    if game_state == "game_over" and key == keys.ESCAPE:
        game_state = "menu"
        reset_game()
        # O herói será reposicionado ao reiniciar o jogo (game_over -> playing)

    # Verifica se está no menu principal
    elif game_state == "menu":
        if key == keys.K_1:  # Iniciar Jogo
            game_state = "playing"
            if game_over_message:  # Resetar posição apenas após game_over
                hero.reset_position()
            if music_on:
                music.play("cruising")
        elif key == keys.K_2:  # Alternar música
            music_on = not music_on
            if music_on:
                music.play("cruising")
            else:
                music.stop()
        elif key == keys.K_3:  # Sair do jogo
            exit()

    # Verifica se está no jogo e permite pulo ou pausa
    elif game_state == "playing":
        if (key == keys.UP or key == keys.SPACE) and hero.on_ground:
            # if key == keys.UP and hero.on_ground:  # Permitir pulo apenas se
            # no chão
            hero.vy = -10
            hero.vy = -10
            hero.vy = -10
            # hero.on_ground = False
            sounds.jump.play()  # Toca o som de pulo
        elif key == keys.ESCAPE:  # Pausar e voltar ao menu
            game_state = "menu"
            music.stop()


flag_animation_timer = 0  # Timer para controlar a animação das bandeiras


def update():
    global camera_x, rocket_active, rocket_final

    if game_state == "playing":
        hero.handle_invulnerability()  # Gerenciar invulnerabilidade
        hero.update_sprite()

        # Controle de movimentação do herói
        if keyboard.left:
            hero.vx = -3
        elif keyboard.right:
            hero.vx = 3
        else:
            hero.vx = 0

        # Aplicar gravidade e pulo
        hero.move()

        # Atualizar posição da câmera para seguir o herói
        camera_x = max(0, min(hero.actor.x - WIDTH // 2,
                       len(level_map[0]) * 18 - WIDTH))

        # Atualizar inimigos
        for enemy in enemies:
            enemy.patrol(platforms)
            enemy.detect_player(hero)
            enemy.shoot(projectiles, hero)

        # Atualizar projéteis
        for projectile in projectiles:
            projectile.move()

        # Verificar colisão com inimigos
        for enemy in enemies:
            if hero.actor.colliderect(enemy.actor):
                hero.take_damage()

        # Verificar colisão com projéteis
        for projectile in projectiles:
            if hero.actor.colliderect(projectile.actor):
                hero.take_damage()
                projectiles.remove(projectile)  # Remover o projétil

    # Movimentar o foguete quando ativo
    if rocket_active:
        rocket_final.y -= 3.5  # Ajuste a velocidade do foguete


pgzrun.go()
