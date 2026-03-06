export interface Task {
  id: number;
  time: string;
  title: string;
  load: number;
  duration: number;
  slack: number;
}

export interface KanbanBoard {
  todo: string[];
  in_progress: string[];
  done: string[];
}

export interface ViewData {
  calendar: Task[];
  kanban: KanbanBoard;
}
