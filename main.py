import pygame
import math

# 초기화
pygame.init()

# 화면 세팅
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Main")

# 색상
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
orange = (255, 127, 0)

# 농구공 초기 설정
ball_radius = 15
ball_x, ball_y = screen_width // 5, screen_height - ball_radius - 100

# 물리값 설정
gravity = 9.8
ball_speed_x = 0
ball_speed_y = 0
shooting = False

# 초기 속도
initial_speed = 0

# 물리 계산 업데이트 간격
physics_interval = 1 / 60

# 백보드 좌표
backboard_width = 0
backboard_height = 0
backboard_x = 0
backboard_y = 0

# 공의 중심점과 마우스 포인터 좌표로 벡터 계산
def get_vector(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return dx, dy

# 계산된 벡터를 정규화
def normalize_vector(dx, dy):
    length = math.sqrt(dx**2 + dy**2)
    if length != 0: # 0으로 나누기 예외처리
        return dx / length, dy / length, length
    else:
        return 0, 0, 0

# 공의 속도 구하기
def get_velocity(dx, dy, length):
    global ball_speed_x, ball_speed_y
    scale_factor = length / 3 # 벡터의 길이를 초기 속도로 지정(너무 크기 때문에 3으로 나눈 값으로 사용)
    ball_speed_x = dx * scale_factor
    ball_speed_y = dy * scale_factor

# 공 위치 업데이트
def move_ball(dt):
    global ball_x, ball_y, ball_speed_x, ball_speed_y

    ball_speed_y += gravity * dt # y축 이동의 경우 중력가속도의 영향

    # 농구공 위치 업데이트
    ball_x += ball_speed_x * dt
    ball_y += ball_speed_y * dt

    # 바닥과 충돌 시 통통 튀어 오름
    if ball_y >= screen_height - ball_radius:
        ball_y = screen_height - ball_radius
        ball_speed_y = -ball_speed_y

# 백보드 그리기 함수
def draw_backboard(isHit):
    global backboard_width
    global backboard_height
    global backboard_x
    global backboard_y

    backboard_width = 10
    backboard_height = 100
    backboard_x = (screen_width - backboard_width) - 200
    backboard_y = screen_height - 300

    pygame.draw.rect(screen, black, (backboard_x, backboard_y, backboard_width, backboard_height))

# 골대 그리기 함수
def draw_hoop(isHit):
    global backboard_width
    global backboard_height
    global backboard_x
    global backboard_y
    
    hoop_width_top = 34
    hoop_width_bottom = 24
    hoop_height = 30
    
    # 골대 좌상하단
    left_top = (backboard_x - 28 - hoop_width_top / 2, backboard_y + 50)  # 상단
    left_bottom = (backboard_x - 28 - hoop_width_bottom / 2, backboard_y + hoop_height + 50)  # 하단

    # 골대 우상하단
    right_top = (backboard_x - 28 + backboard_width + hoop_width_top / 2, backboard_y + 50)  # 상단
    right_bottom = (backboard_x - 28 + backboard_width + hoop_width_bottom / 2, backboard_y + hoop_height + 50)  # 하단

    hoop_points = [left_top, right_top, right_bottom, left_bottom]
    
    hoop_color = black
    if isHit:
        hoop_color = red

    pygame.draw.polygon(screen, hoop_color, hoop_points)

# 백보드 콜리전
def backboard_collision():
    global ball_x, ball_y, ball_speed_x, ball_speed_y

    # 백보드 위치
    global backboard_width
    global backboard_height
    global backboard_x
    global backboard_y
    
    # 백보드의 충돌 영역
    backboard_left = backboard_x
    backboard_right = backboard_x + backboard_width
    backboard_top = backboard_y
    backboard_bottom = backboard_y + backboard_height

    # 농구공의 충돌 영역
    ball_left = ball_x - ball_radius
    ball_right = ball_x + ball_radius
    ball_top = ball_y - ball_radius
    ball_bottom = ball_y + ball_radius

    # 백보드와 농구공 충돌 감지
    if (ball_right > backboard_left and ball_left < backboard_right and
        ball_bottom > backboard_top and ball_top < backboard_bottom):
        
        # 반사 벡터 계산 (속도 벡터를 기준으로 반사)
        if ball_speed_x != 0: # 수평 충돌 (백보드의 세로면과 충돌)
            normal_x = 1 # 세로면의 법선 벡터는 (1, 0)
            normal_y = 0
        elif ball_speed_y != 0: # 수직 충돌 (백보드의 상하단면과 충돌)
            normal_x = 0 # 수평면의 법선 벡터는 (0, 1)
            normal_y = 1
        else:
            return False

        # 입사 벡터 (공의 속도)
        incident_x = ball_speed_x
        incident_y = ball_speed_y

        # 입사 벡터와 법선 벡터의 내적 계산
        dot_product = incident_x * normal_x + incident_y * normal_y

        # 반사 벡터 계산 (reflection = incident - 2 * (incident · normal) * normal)
        ball_speed_x = incident_x - 2 * dot_product * normal_x
        ball_speed_y = incident_y - 2 * dot_product * normal_y
        
        return True

    return False

# 골 판정을 위한 콜리전
def goal_collision():
    global ball_x, ball_y, ball_radius
    global backboard_x, backboard_y, backboard_width

    # 골대의 상단 좌표 및 크기 설정
    hoop_width_top = 34
    hoop_x_start = backboard_x - 28 - hoop_width_top / 2
    hoop_x_end = hoop_x_start + hoop_width_top
    hoop_y_top = backboard_y + 50
    hoop_y_bottom = hoop_y_top + 30

    # 농구공 충돌 영역
    ball_left = ball_x - ball_radius
    ball_right = ball_x + ball_radius
    ball_top = ball_y - ball_radius
    ball_bottom = ball_y + ball_radius

    # 골대와 공의 충돌 판정 및 골 판정 영역 설정
    if (hoop_x_start <= ball_left and ball_right <= hoop_x_end) and\
        (ball_top >= hoop_y_top) and (ball_bottom >= hoop_y_bottom):
        print("hello")
        return True
    return False

# 공을 초기 위치로 다시 세팅
def reset_game():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, shooting
    ball_x, ball_y = screen_width // 5, screen_height - ball_radius - 100
    ball_speed_x = 0
    ball_speed_y = 0
    shooting = False

# 메인 함수
def main():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, shooting

    clock = pygame.time.Clock()
    running = True
    physics_time_accumulator = 0 # 물리 계산 용 시간 축적 변수

    isHit = False # 충돌 체크    

    while running:
        dt = clock.tick(60) / 300 # 프레임 간 시간 간격
        physics_time_accumulator += dt

        screen.fill(white)
        
        draw_backboard(isHit)
        draw_hoop(isHit)
        
        # 농구공 그리기
        pygame.draw.circle(screen, orange, (ball_x, ball_y), ball_radius)

        # 농구공이 백보드에 닿았는지 확인
        isHit = goal_collision()
        backboard_collision()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and not shooting:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx, dy = get_vector(ball_x, ball_y, mouse_x, mouse_y)
                dx, dy, length = normalize_vector(dx, dy)
                get_velocity(dx, dy, length) # 초기 속도(벡터의 길이로 계산)
                shooting = True

            # r 키 입력하면 리셋
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()

        # 물리 계산이 일정 시간 간격으로 이루어지도록 처리
        while physics_time_accumulator >= physics_interval:
            if shooting:
                move_ball(dt) # 물리 계산에 dt를 반영
            physics_time_accumulator -= physics_interval

        # 공이 화면 밖으로 나가면 리셋
        if ball_y > screen_height or ball_x < 0 or ball_x > screen_width:
            reset_game()

        # 화면 업데이트
        pygame.display.update()

    pygame.quit()

# 시뮬 시작
if __name__ == '__main__':
    main()