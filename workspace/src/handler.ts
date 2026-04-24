/**
 * HTTP 请求处理器 —— 用于测试 AI 编码助手
 */

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T | null;
}

interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "user" | "viewer";
  createdAt: Date;
}

const users: Map<number, User> = new Map();

function generateId(): number {
  return Math.floor(Math.random() * 1000000);
}

export function getUser(id: number): ApiResponse<User> {
  const user = users.get(id);
  if (!user) {
    return { code: 404, message: "用户不存在", data: null };
  }
  return { code: 200, message: "OK", data: user };
}

export function createUser(name: string, email: string): ApiResponse<User> {
  if (!name || !email) {
    return { code: 400, message: "name 和 email 不能为空", data: null };
  }

  const id = generateId();
  const user: User = {
    id,
    name,
    email,
    role: "user",
    createdAt: new Date(),
  };
  users.set(id, user);

  return { code: 201, message: "创建成功", data: user };
}

export function listUsers(page: number = 1, size: number = 20): ApiResponse<User[]> {
  const all = Array.from(users.values());
  const start = (page - 1) * size;
  const paged = all.slice(start, start + size);

  return {
    code: 200,
    message: "OK",
    data: paged,
  };
}

export function deleteUser(id: number): ApiResponse<null> {
  if (!users.has(id)) {
    return { code: 404, message: "用户不存在", data: null };
  }
  users.delete(id);
  return { code: 200, message: "删除成功", data: null };
}
