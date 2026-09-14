# Frontend 鏡像：Vite 建置靜態檔，Nginx 提供 SPA 與 /ws 反代。
# Apple Silicon 優先走 image 的 linux/arm64。

FROM node:20-alpine AS build

WORKDIR /app

# 留空時前端自行用同源位址，由 Nginx 的 /ws 反代到 backend:8000；
# 需要指向別的位址時再從 compose 帶入。
ARG VITE_WS_URL=
ENV VITE_WS_URL=$VITE_WS_URL

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
