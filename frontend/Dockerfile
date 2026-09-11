# Frontend 鏡像：Vite 建置靜態檔，Nginx 提供 SPA 與 /ws 反代。
# Apple Silicon 優先走 image 的 linux/arm64。

FROM node:20-alpine AS build

WORKDIR /app

# Production 瀏覽器連同源 Nginx（:8080），再反代到 backend:8000。
ARG VITE_WS_URL=ws://localhost:8080/ws/gps
ENV VITE_WS_URL=$VITE_WS_URL

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
