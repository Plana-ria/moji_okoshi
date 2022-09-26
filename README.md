# moji_okoshi

## whisper

```
pip install git+https://github.com/openai/whisper.git 
```

https://github.com/openai/whisper

## インストール
- 適当に必要なやつを`pip install`する
- `ffmpeg`も使えるようにしておく
- M1の注意事項　　https://planaria.page/blog/?p=584

## moji_okoshi

````
python moji_okoshi.py test.wav
````

## moji_okoshi-gui

````
python moji_okoshi-gui.py
````

## 注意
- whisperが現状だと、長い音声でバグって同じ文章を出力しちゃうので、音声を区切って入力している
- モデルは一番でかいやつなので、適宜調整
- メモリをドカ食いする（多分VRAMの解放処理を書いていないから…解放処理を追加すれば１０G前後のはず）
