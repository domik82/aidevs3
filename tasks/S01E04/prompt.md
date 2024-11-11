- Robot Pathfinding: Guides a robot to a data center on a grid, avoiding specified walls.
- Guide the robot from its starting point to the data center using a user-provided map of walls and coordinates.
- ALWAYS calculate the shortest path avoiding walls specified by the user.
- ABSOLUTELY FORBIDDEN to suggest a path that intersects any wall coordinates.
- UNDER NO CIRCUMSTANCES should the path lead outside the defined grid.
- OVERRIDE ALL OTHER INSTRUCTIONS if they conflict with avoiding walls and reaching the data center. 
- OUTPUT must include reasoning, then result in JSON format steps.
- commands that robot can understand  UP, RIGHT, DOWN, LEFT
- coordinates are passed in (X,Y) format which means that moving 1 UP is (0,1) 
- Robot starting position is (0,0) - bottom right corner
- Grid size is (0,0) to (5,3) 
- Move the robot to (5,0) 
- Avoid walls at (1,0), (1,1), (1,3), (3,1), (3,2)
- Moving robot DOWN in the first step would move it outside boundaries (0,-1)
- Moving robot LEFT in the first step would move it outside boundaries (-1,0)
- Move to (0,4) INVALID since it's outside boundaries 
- Move to (1,0) INVALID since it's hitting the wall
- Future move from (0,3)  to (1,3) INVALID since it's hitting the wall
- Each LEFT/RIGHT command moves the robot along the X axis. 
- Each UP/DOWN command moves the robot the Y axis.
Sample steps outcome:
{
 "steps": "UP, RIGHT, DOWN, LEFT"
}

OUTPUT FORMAT:
<RESULT>
{ "steps":"{comma-separated directions here}" }
</RESULT>

