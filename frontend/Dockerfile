# Use Node.js 22 on Alpine Linux
FROM node:22-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose the development server port
EXPOSE 5173

# Run the dev server, binding to 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host"]
