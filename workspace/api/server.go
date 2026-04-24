// Package api —— 用于测试 AI 编码助手
package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"sync"
	"time"
)

// Task 表示一个待办任务
type Task struct {
	ID        int       `json:"id"`
	Title     string    `json:"title"`
	Done      bool      `json:"done"`
	CreatedAt time.Time `json:"created_at"`
}

// TaskStore 线程安全的任务存储
type TaskStore struct {
	mu     sync.RWMutex
	tasks  map[int]*Task
	nextID int
}

// NewTaskStore 创建新的任务存储
func NewTaskStore() *TaskStore {
	return &TaskStore{
		tasks:  make(map[int]*Task),
		nextID: 1,
	}
}

// Create 创建任务
func (s *TaskStore) Create(title string) *Task {
	s.mu.Lock()
	defer s.mu.Unlock()

	task := &Task{
		ID:        s.nextID,
		Title:     title,
		Done:      false,
		CreatedAt: time.Now(),
	}
	s.tasks[task.ID] = task
	s.nextID++
	return task
}

// Get 获取任务
func (s *TaskStore) Get(id int) (*Task, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	task, ok := s.tasks[id]
	if !ok {
		return nil, fmt.Errorf("任务 %d 不存在", id)
	}
	return task, nil
}

// List 列出所有任务
func (s *TaskStore) List() []*Task {
	s.mu.RLock()
	defer s.mu.RUnlock()

	result := make([]*Task, 0, len(s.tasks))
	for _, task := range s.tasks {
		result = append(result, task)
	}
	return result
}

// Toggle 切换任务完成状态
func (s *TaskStore) Toggle(id int) (*Task, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	task, ok := s.tasks[id]
	if !ok {
		return nil, fmt.Errorf("任务 %d 不存在", id)
	}
	task.Done = !task.Done
	return task, nil
}

// Delete 删除任务
func (s *TaskStore) Delete(id int) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	if _, ok := s.tasks[id]; !ok {
		return fmt.Errorf("任务 %d 不存在", id)
	}
	delete(s.tasks, id)
	return nil
}

// ServeHTTP 启动 HTTP 服务
func ServeHTTP(store *TaskStore, port int) error {
	mux := http.NewServeMux()

	mux.HandleFunc("/tasks", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			json.NewEncoder(w).Encode(store.List())
		case http.MethodPost:
			var req struct{ Title string `json:"title"` }
			json.NewDecoder(r.Body).Decode(&req)
			task := store.Create(req.Title)
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(task)
		default:
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	})

	mux.HandleFunc("/tasks/", func(w http.ResponseWriter, r *http.Request) {
		idStr := r.URL.Path[len("/tasks/"):]
		id, err := strconv.Atoi(idStr)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		switch r.Method {
		case http.MethodGet:
			task, err := store.Get(id)
			if err != nil {
				w.WriteHeader(http.StatusNotFound)
				return
			}
			json.NewEncoder(w).Encode(task)
		case http.MethodPatch:
			task, err := store.Toggle(id)
			if err != nil {
				w.WriteHeader(http.StatusNotFound)
				return
			}
			json.NewEncoder(w).Encode(task)
		case http.MethodDelete:
			err := store.Delete(id)
			if err != nil {
				w.WriteHeader(http.StatusNotFound)
				return
			}
			w.WriteHeader(http.StatusNoContent)
		default:
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	})

	addr := fmt.Sprintf(":%d", port)
	return http.ListenAndServe(addr, mux)
}
