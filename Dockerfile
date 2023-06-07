# develop stage
FROM docker.uclv.cu/node:16-alpine as develop-stage
WORKDIR /frontend
COPY ./frontend/package*.json /frontend/package*.json
RUN yarn global add @quasar/cli
COPY ./frontend /frontend
# build stage
FROM develop-stage as build-stage
# RUN cd frontend
RUN yarn
# RUN quasar build
# production stage
#FROM docker.uclv.cu/nginx:1.17.5-alpine as production-stage
#COPY --from=build-stage /frontend/dist/spa /usr/share/nginx/html
#EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]
CMD [ "quasar", "dev" ]