# eatda-be
### Project Settings

0. folder structure
   ```
   eatda-be
   ├─accounts
   │  └─migrations
   ├─config
   │  ├─docker
   │  ├─nginx
   │  └─scripts
   ├─diets
   │  └─migrations
   ├─eatda_be
   │  └─settings
   └─users
      └─migrations
   ```
1. add env file
- create `.env` file in `eatda-be/`
- create `.env.prod` file in `eatda-be/`
- add `pem` key in `eatda-be/`
- env file & pem key exist in [this drive link](https://iewha-my.sharepoint.com/:f:/g/personal/bsa0322_i_ewha_ac_kr/EkOMmPvdYehInVSvRAhaw3EB3Nyu_tWhVvym_DsAmabZ9g)

2. docker build
  - for the first time
  ```
  docker-compose build
  ```
  
3. run project
   ```shell
   docker-compose up
   ```
