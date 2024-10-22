import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import pandas as pd
import time
from matplotlib.colors import ListedColormap

st.title("ライフゲーム！")

class LifeGame:
    def __init__(self, csv_file):
        if isinstance(csv_file, str):
            # ファイルパスから読み込む
            df = pd.read_csv(csv_file, header=None, dtype=str)
        else:
            # アップロードされたファイルから読み込む
            df = pd.read_csv(csv_file, header=None, dtype=str)
        # 空白を削除
        df = df.replace('', np.nan).fillna('0')
        # DataFrameをnumpy配列に変換
        self.field = df.applymap(lambda x: 1 if x in ['●', '1'] else 0).values
        # 最初と最後の行がすべて0の場合は削除
        if np.all(self.field[0] == 0) and np.all(self.field[-1] == 0):
            self.field = self.field[1:-1]
        # フィールドのサイズを取得
        self.rows, self.cols = self.field.shape
        st.info(f"CSVファイルのサイズ: {self.rows}行 x {self.cols}列")
     
    # 生存チェック
    def check(self, y, x):
        cnt = 0
        neighbors = [(-1, -1), (0, -1), (1, -1),
                     (1, 0), (1, 1), (0, 1),
                     (-1, 1), (-1, 0)]
        for dy, dx in neighbors:
            yy, xx = (y + dy) % self.rows, (x + dx) % self.cols  # グリッドのラップアラウンド
            cnt += self.field[yy, xx]
        return cnt

    def evolution(self):
        next_field = np.zeros((self.rows, self.cols), dtype=int)
        for y in range(self.rows):
            for x in range(self.cols):
                n = self.check(y, x)
                s = self.field[y, x]
                if s == 0 and n == 3:
                    next_field[y, x] = 1
                elif s == 1 and 2 <= n <= 3:
                    next_field[y, x] = 1
                else:
                    next_field[y, x] = 0
        self.field = next_field
        return self.field

    def get_field(self):
        return self.field

step = st.number_input("ステップ数", min_value=1, max_value=10000, value=100)

# 事前定義されたCSVファイルのリスト
predefined_csv_files = {
    'パターン1': 'dat00.csv',
    'パターン2': 'dat01.csv',
    'パターン3': 'dat03.csv',
    'パターン4': 'dat04.csv',
    'パターン5': 'dat05.csv'
}

st.write("### 事前定義されたパターンを選択するか、CSVファイルをアップロードしてください")

# 事前定義されたパターンの選択
selected_pattern = st.radio("パターンを選択", list(predefined_csv_files.keys()))

# ファイルアップローダー
uploaded_file = st.file_uploader("またはCSVファイルをアップロード", type="csv")

start_button = st.button("スタート")
pause_button = st.button("一時停止")
reset_button = st.button("リセット")

# セッションステートの初期化
if 'paused' not in st.session_state:
    st.session_state.paused = False
if 'game' not in st.session_state:
    st.session_state.game = None
if 'step_count' not in st.session_state:
    st.session_state.step_count = 0

# スタートボタンが押された場合
if start_button:
    # アップロードされたファイルを使用
    if uploaded_file is not None:
        csv_file = uploaded_file
    else:
        # 選択された事前定義ファイルを使用
        csv_file = predefined_csv_files[selected_pattern]
    # ゲームの初期化
    st.session_state.game = LifeGame(csv_file)
    st.session_state.paused = False
    st.session_state.step_count = 0

# 一時停止ボタンが押された場合
if pause_button:
    st.session_state.paused = not st.session_state.paused

# リセットボタンが押された場合
if reset_button:
    st.session_state.game = None
    st.session_state.paused = False
    st.session_state.step_count = 0

# ゲームが初期化されている場合
if st.session_state.game is not None:
    game = st.session_state.game
    cmap = ListedColormap(['yellow', 'purple'])

    # プロットの設定
    fig, ax = plt.subplots()
    plt.axis('off')  # 軸を非表示にする

    img = ax.imshow(game.field, cmap=cmap)
    # プレースホルダーの作成
    placeholder = st.empty()

    # シミュレーションの実行
    while st.session_state.step_count < step:
        if st.session_state.paused:
            # 一時停止中は何もしない
            time.sleep(0.1)
            continue
        else:
            game.evolution()
            img.set_data(game.field)      # 画像データを更新
            placeholder.pyplot(fig)       # プレースホルダー内のプロットを更新           
            st.session_state.step_count += 1
            time.sleep(0.1)               # アニメーションの速度を制御

    st.write("シミュレーションが終了しました。")
