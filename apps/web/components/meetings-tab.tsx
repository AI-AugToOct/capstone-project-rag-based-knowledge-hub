import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Calendar, Clock, Plus } from "lucide-react"
import { cn } from "@/lib/utils"

const upcomingMeetings = [
  {
    id: 1,
    title: "Q4 Project Sync",
    date: "October 1, 2025",
    time: "3:00 PM",
    participants: [
      { name: "John Smith", avatar: "/placeholder.svg?height=32&width=32" },
      { name: "Sarah Lee", avatar: "/placeholder.svg?height=32&width=32" },
      { name: "Mike Chen", avatar: "/placeholder.svg?height=32&width=32" },
    ],
  },
  {
    id: 2,
    title: "Design Review Meeting",
    date: "October 3, 2025",
    time: "10:00 AM",
    participants: [
      { name: "Emma Davis", avatar: "/placeholder.svg?height=32&width=32" },
      { name: "Alex Johnson", avatar: "/placeholder.svg?height=32&width=32" },
    ],
  },
  {
    id: 3,
    title: "Sprint Planning",
    date: "October 5, 2025",
    time: "2:00 PM",
    participants: [
      { name: "Lisa Wang", avatar: "/placeholder.svg?height=32&width=32" },
      { name: "John Smith", avatar: "/placeholder.svg?height=32&width=32" },
      { name: "Sarah Lee", avatar: "/placeholder.svg?height=32&width=32" },
      { name: "Mike Chen", avatar: "/placeholder.svg?height=32&width=32" },
    ],
  },
  {
    id: 4,
    title: "Client Presentation",
    date: "October 8, 2025",
    time: "11:00 AM",
    participants: [
      { name: "Emma Davis", avatar: "/placeholder.svg?height=32&width=32" },
      { name: "Alex Johnson", avatar: "/placeholder.svg?height=32&width=32" },
      { name: "Lisa Wang", avatar: "/placeholder.svg?height=32&width=32" },
    ],
  },
]

const calendarDays = [
  { day: 1, hasMeeting: true, isToday: true },
  { day: 2, hasMeeting: false, isToday: false },
  { day: 3, hasMeeting: true, isToday: false },
  { day: 4, hasMeeting: false, isToday: false },
  { day: 5, hasMeeting: true, isToday: false },
  { day: 6, hasMeeting: false, isToday: false },
  { day: 7, hasMeeting: false, isToday: false },
  { day: 8, hasMeeting: true, isToday: false },
  { day: 9, hasMeeting: false, isToday: false },
  { day: 10, hasMeeting: false, isToday: false },
  { day: 11, hasMeeting: false, isToday: false },
  { day: 12, hasMeeting: false, isToday: false },
  { day: 13, hasMeeting: false, isToday: false },
  { day: 14, hasMeeting: false, isToday: false },
  { day: 15, hasMeeting: true, isToday: false },
  { day: 16, hasMeeting: false, isToday: false },
  { day: 17, hasMeeting: false, isToday: false },
  { day: 18, hasMeeting: false, isToday: false },
  { day: 19, hasMeeting: false, isToday: false },
  { day: 20, hasMeeting: false, isToday: false },
  { day: 21, hasMeeting: false, isToday: false },
  { day: 22, hasMeeting: true, isToday: false },
  { day: 23, hasMeeting: false, isToday: false },
  { day: 24, hasMeeting: false, isToday: false },
  { day: 25, hasMeeting: false, isToday: false },
  { day: 26, hasMeeting: false, isToday: false },
  { day: 27, hasMeeting: false, isToday: false },
  { day: 28, hasMeeting: false, isToday: false },
  { day: 29, hasMeeting: true, isToday: false },
  { day: 30, hasMeeting: false, isToday: false },
  { day: 31, hasMeeting: false, isToday: false },
]

export function MeetingsTab() {
  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-foreground">Meetings</h2>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Schedule New Meeting
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 p-6 bg-background overflow-auto">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Upcoming Meetings List */}
            <div className="lg:col-span-1">
              <h3 className="text-base font-semibold text-foreground mb-4">Upcoming Meetings</h3>
              <div className="space-y-3">
                {upcomingMeetings.map((meeting) => (
                  <div
                    key={meeting.id}
                    className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <h4 className="font-semibold text-foreground mb-2">{meeting.title}</h4>
                    <div className="space-y-2 mb-3">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        {meeting.date}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        {meeting.time}
                      </div>
                    </div>
                    <div className="flex -space-x-2">
                      {meeting.participants.map((participant, idx) => (
                        <Avatar key={idx} className="h-7 w-7 border-2 border-card">
                          <AvatarImage src={participant.avatar || "/placeholder.svg"} />
                          <AvatarFallback className="text-xs">
                            {participant.name
                              .split(" ")
                              .map((n) => n[0])
                              .join("")}
                          </AvatarFallback>
                        </Avatar>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Calendar View */}
            <div className="lg:col-span-2">
              <div className="bg-card border border-border rounded-lg p-6">
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-foreground">October 2025</h3>
                </div>

                {/* Calendar Grid */}
                <div className="grid grid-cols-7 gap-2">
                  {/* Day Headers */}
                  {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                    <div key={day} className="text-center text-sm font-medium text-muted-foreground py-2">
                      {day}
                    </div>
                  ))}

                  {/* Empty cells for alignment (October 2025 starts on Wednesday) */}
                  {[...Array(3)].map((_, idx) => (
                    <div key={`empty-${idx}`} className="aspect-square" />
                  ))}

                  {/* Calendar Days */}
                  {calendarDays.map((dayInfo) => (
                    <div
                      key={dayInfo.day}
                      className={cn(
                        "aspect-square flex flex-col items-center justify-center rounded-lg border border-border relative hover:bg-muted/50 transition-colors cursor-pointer",
                        dayInfo.isToday && "bg-primary text-primary-foreground font-semibold border-primary",
                      )}
                    >
                      <span className="text-sm">{dayInfo.day}</span>
                      {dayInfo.hasMeeting && <div className="absolute bottom-1 w-1.5 h-1.5 rounded-full bg-blue-500" />}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
