FROM node:16-alpine as build-stage
WORKDIR /app
RUN set -eux \
    & apk add \
    --no-cache \
    nodejs \
    yarn
COPY . .
RUN yarn
RUN yarn build

FROM nginx:1.23-alpine as production-stage
COPY --from=build-stage /app/build /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]