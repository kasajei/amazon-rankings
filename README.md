# https://amazon-rankings.appspot.com
Amazonのランキングをスクレイピングして

- ランキングの履歴の表示
- 良いタイミングで通知(Twitter)

とかしたい

# README.md from [scaffold](https://github.com/potatolondon/djangae-scaffold) 
## 新しいライブラリを入れる時はrequirements.txtに記載して
```bash
pip install -r requirements.txt -t sitepackages -I

```


## Deployment

Create a Google App Engine project. Edit `app.yaml` and change `application: djangae-scaffold` to `application: your-app-id`. Then, if you're in the `djangae-scaffold` directory, run:

```bash
# dev
$ gcloud  app deploy --version 1 --project amazon-rankings
```