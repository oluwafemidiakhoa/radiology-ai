# Stage 1: Build the React app
FROM node:16-alpine as build

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the app and build
COPY . .
RUN npm run build

# Stage 2: Serve the build with nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 and start nginx
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
