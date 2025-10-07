import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus } from "lucide-react"

const tasks = {
  todo: [
    {
      id: 1,
      title: "Develop user authentication flow",
      description: "Implement secure login and registration system",
      dueDate: "Oct 15",
      project: "Project Phoenix",
      assignee: { name: "John Smith", avatar: "/placeholder.svg?height=32&width=32" },
    },
    {
      id: 2,
      title: "Design new dashboard layout",
      description: "Create wireframes and mockups for the main dashboard",
      dueDate: "Oct 12",
      project: "Project Atlas",
      assignee: { name: "Sarah Lee", avatar: "/placeholder.svg?height=32&width=32" },
    },
  ],
  inProgress: [
    {
      id: 3,
      title: "API integration for payment gateway",
      description: "Connect Stripe API for payment processing",
      dueDate: "Oct 8",
      project: "Project Phoenix",
      assignee: { name: "Mike Chen", avatar: "/placeholder.svg?height=32&width=32" },
    },
    {
      id: 4,
      title: "Write technical documentation",
      description: "Document API endpoints and usage examples",
      dueDate: "Oct 10",
      project: "Project Atlas",
      assignee: { name: "Emma Davis", avatar: "/placeholder.svg?height=32&width=32" },
    },
  ],
  done: [
    {
      id: 5,
      title: "Set up CI/CD pipeline",
      description: "Configure automated testing and deployment",
      dueDate: "Oct 1",
      project: "Project Phoenix",
      assignee: { name: "Alex Johnson", avatar: "/placeholder.svg?height=32&width=32" },
    },
    {
      id: 6,
      title: "Database schema design",
      description: "Design and implement database structure",
      dueDate: "Sep 28",
      project: "Project Atlas",
      assignee: { name: "Lisa Wang", avatar: "/placeholder.svg?height=32&width=32" },
    },
  ],
}

function TaskCard({ task }: { task: (typeof tasks.todo)[0] }) {
  return (
    <div className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow">
      <h4 className="font-semibold text-foreground mb-2 leading-snug">{task.title}</h4>
      <p className="text-sm text-muted-foreground mb-3 leading-relaxed">{task.description}</p>
      <div className="flex items-center justify-between">
        <div className="space-y-1.5">
          <p className="text-xs text-muted-foreground">Due {task.dueDate}</p>
          <Badge variant="secondary" className="text-xs">
            {task.project}
          </Badge>
        </div>
        <Avatar className="h-8 w-8">
          <AvatarImage src={task.assignee.avatar || "/placeholder.svg"} />
          <AvatarFallback>
            {task.assignee.name
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </AvatarFallback>
        </Avatar>
      </div>
    </div>
  )
}

export function ProjectsTab() {
  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-foreground">Projects & Tasks</h2>
          <div className="flex items-center gap-3">
            <Select defaultValue="all">
              <SelectTrigger className="w-48 bg-background">
                <SelectValue placeholder="Filter by Project" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Projects</SelectItem>
                <SelectItem value="phoenix">Project Phoenix</SelectItem>
                <SelectItem value="atlas">Project Atlas</SelectItem>
              </SelectContent>
            </Select>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              New Task
            </Button>
          </div>
        </div>
      </header>

      {/* Kanban Board */}
      <div className="flex-1 p-6 bg-background overflow-auto">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* To Do Column */}
            <div className="flex flex-col">
              <div className="bg-card border border-border rounded-lg p-4 mb-4">
                <h3 className="font-semibold text-foreground flex items-center justify-between">
                  To Do
                  <Badge variant="secondary" className="ml-2">
                    {tasks.todo.length}
                  </Badge>
                </h3>
              </div>
              <div className="space-y-3">
                {tasks.todo.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>

            {/* In Progress Column */}
            <div className="flex flex-col">
              <div className="bg-card border border-border rounded-lg p-4 mb-4">
                <h3 className="font-semibold text-foreground flex items-center justify-between">
                  In Progress
                  <Badge variant="secondary" className="ml-2">
                    {tasks.inProgress.length}
                  </Badge>
                </h3>
              </div>
              <div className="space-y-3">
                {tasks.inProgress.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>

            {/* Done Column */}
            <div className="flex flex-col">
              <div className="bg-card border border-border rounded-lg p-4 mb-4">
                <h3 className="font-semibold text-foreground flex items-center justify-between">
                  Done
                  <Badge variant="secondary" className="ml-2">
                    {tasks.done.length}
                  </Badge>
                </h3>
              </div>
              <div className="space-y-3">
                {tasks.done.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
