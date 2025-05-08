import threading
import time
import os
import sys
import select
import tty
import termios
import pygame



cockie = 1000.0
auto_cockie = 0.0
update_ui_sec = 0.1
auto_cockie_sec = 1.0
menu_state = 0


pygame.init()
pygame.mixer.init() # ここで音を扱うためのinit
h_sound = pygame.mixer.Sound("h.wav")
m_sound = pygame.mixer.Sound("m.wav")
l_sound = pygame.mixer.Sound("l.wav")



# ANSIエスケープシーケンス
CSI = "\033["
CLEAR_SCREEN = CSI + "2J"
MOVE_CURSOR_TOP_LEFT = CSI + "1;1H"
GREEN_TEXT = CSI + "32m"
YELLOW_TEXT = CSI + "33m"
MAGENTA_TEXT = CSI + "35m"
WHITE_TEXT = CSI + "37m"
RESET_COLOR = CSI + "0m"


def update_ui():
    global cockie, menu_state, auto_cockie
    #print(f"cockie = : {cockie}")

    # 画面をクリアしてカーソルを左上に移動し、cockieの値を緑色で表示
    print(f"{CLEAR_SCREEN}{MOVE_CURSOR_TOP_LEFT}", end="") # 画面全体をクリアする場合
    # print(f"{GREEN_TEXT}cockie = : {cockie}{RESET_COLOR}", flush=True)

    # 1行目: タイトルの一部
    print(f"{CSI}1;1H{CSI}K{YELLOW_TEXT}Cock{RESET_COLOR}", flush=True)
    # 2行目: タイトルの一部
    print(f"{CSI}1;5H{CSI}K{WHITE_TEXT}Wii{RESET_COLOR}", flush=True)
    # 3行目: タイトルの一部
    print(f"{CSI}1;8H{CSI}K{GREEN_TEXT}Clicker{RESET_COLOR}", flush=True)

    print(f"{CSI}2;1H{CSI}K{WHITE_TEXT}---------------------{RESET_COLOR}", flush=True)

    # 5行目あたりに cockie の値を表示 (少し間を空ける)
    print(f"{CSI}5;1H{CSI}K{YELLOW_TEXT}Cockies : {cockie:.0f}{RESET_COLOR}", flush=True)


    if(menu_state == 0):
        print(f"{CSI}10;1H{CSI}K{WHITE_TEXT}->{RESET_COLOR}", flush=True)
    elif(menu_state == 1):
        print(f"{CSI}11;1H{CSI}K{WHITE_TEXT}->{RESET_COLOR}", flush=True)
    elif(menu_state == 2):
        print(f"{CSI}12;1H{CSI}K{WHITE_TEXT}->{RESET_COLOR}", flush=True)


    print(f"{CSI}10;4H{CSI}K{WHITE_TEXT}Upgrade Clicker(20 coockies){RESET_COLOR}", flush=True)
    print(f"{CSI}11;4H{CSI}K{WHITE_TEXT}Upgrade Auto Clicker(100 coockies){RESET_COLOR}", flush=True)
    print(f"{CSI}12;4H{CSI}K{WHITE_TEXT}Buy Potato (50 coockies){RESET_COLOR}", flush=True)

    print(f"{CSI}15;1H{CSI}K{WHITE_TEXT}menu_state : {menu_state}{RESET_COLOR}", flush=True)
    print(f"{CSI}16;1H{CSI}K{WHITE_TEXT}auto_cockie : {auto_cockie}{RESET_COLOR}", flush=True)

    print(f"{CSI}17;1H{CSI}K{WHITE_TEXT}W = Up{RESET_COLOR}", flush=True)
    print(f"{CSI}18;1H{CSI}K{WHITE_TEXT}S = Down{RESET_COLOR}", flush=True)
    print(f"{CSI}19;1H{CSI}K{WHITE_TEXT}L = Click{RESET_COLOR}", flush=True)


    #タイマー再設定
    timer = threading.Timer(update_ui_sec, update_ui)
    timer.daemon = True  # メインプログラム終了時にタイマースレッドも終了するようにする
    timer.start()

#1秒毎にクッキーを追加
def auto_cockie_count():
    global cockie, menu_state, auto_cockie, auto_cockie_sec

    cockie = cockie + auto_cockie

    #タイマー再設定
    timer = threading.Timer(auto_cockie_sec, auto_cockie_count)
    timer.daemon = True  # メインプログラム終了時にタイマースレッドも終了するようにする
    timer.start()







# --- メイン処理 ---
if __name__ == "__main__":
    # 最初に画面をクリアし、カーソルを非表示にする
    print(f"{CLEAR_SCREEN}{CSI}?25l", end="")

    # ターミナルの元の設定を保存
    old_settings = termios.tcgetattr(sys.stdin)

    #update_uiのタイマー設定
    initial_timer = threading.Timer(update_ui_sec, update_ui)
    initial_timer.daemon = True
    initial_timer.start()


    try:
        # ターミナルをcbreakモードに設定 (キー入力を即座に受け取る)
        tty.setcbreak(sys.stdin.fileno())

        add_cockie = 1

        while True:
            # キー入力があるかチェック (タイムアウト0秒で非ブロッキング)
            if select.select([sys.stdin], [], [], 0.0) == ([sys.stdin], [], []):
                key = sys.stdin.read(1)
                if key.lower() == 'l':  # 'l' または 'L' キーが押されたら
                    cockie += add_cockie
                    #print("\a", flush=True) # ビープ音を鳴らす
                    m_sound.play()

                elif key.lower() == 'w': # 'w'キーでmenu_stateをインクリメント
                    menu_state -= 1
                    if menu_state < 0:  # メニュー項目は0, 1, 2なので、最大値は2
                        menu_state = 0  # 上限を超えたら2に留める (または0に戻して循環させることも可能)
                elif key.lower() == 's': # 's'キーでmenu_stateをデクリメント
                    menu_state += 1
                    if menu_state > 2:  # 最小値は0
                        menu_state = 2  # 下限を下回ったら0に留める (または2に戻して循環させることも可能)

                elif key == '\r' or key == '\n': # エンターキーが押されたら
                    #メニューステート処理
                    #Upgrade Clicker(20 coockies) = 0
                    #Upgrade Auto Clicker(100 coockies) = 1
                    if menu_state == 0:
                        if cockie >= 20:
                            cockie -=20
                            add_cockie += 1
                            h_sound.play()
                        else:
                            l_sound.play()

                    elif menu_state == 1: # Upgrade Auto Clicker
                        if cockie >= 100:
                            cockie -= 100
                            auto_cockie += 0.1
                            h_sound.play()
                            timer = threading.Timer(auto_cockie_sec, auto_cockie_count)
                            timer.daemon = True  # メインプログラム終了時にタイマースレッドも終了するようにする
                            timer.start()
                        else:
                            l_sound.play()


                elif key.lower() == 'q': # 'q' キーで終了
                    break
            
            time.sleep(0.01) # メインスレッドのループ速度調整

    except KeyboardInterrupt:
        # Ctrl+Cが押された場合もここに来る
        pass # finallyブロックで終了処理を行う
    finally:
        # ターミナルの設定を元に戻す
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        # カーソルを再表示し、色をリセット、改行してプロンプトを見やすくする
        print(f"{CSI}?25h{RESET_COLOR}\n終了します。")

        # os._exit(0) # 必要であればスレッドを強制終了 (通常は不要)
