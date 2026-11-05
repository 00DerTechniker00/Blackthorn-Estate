"""Find a descending footpath near the surveyed surface, with at most one block per step."""
import heapq

def route(terrain):
    x0,_,z0,_=terrain['bounds'];start=(-640,129,772);goal=(-581,63,754)
    def height(x,z):return terrain['heights'][z-z0][x-x0]
    def heuristic(p):return max(abs(p[0]-goal[0])+abs(p[2]-goal[2]),p[1]-goal[1])
    queue=[(heuristic(start),0,start)];cost={start:0};parent={}
    while queue:
        _,c,p=heapq.heappop(queue)
        if c!=cost[p]:continue
        if p==goal:
            result=[p]
            while result[-1]!=start:result.append(parent[result[-1]])
            result.reverse()
            if len({(x,z) for x,y,z in result})!=len(result):raise ValueError('Path overlaps itself vertically')
            return result
        x,y,z=p
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            xx,zz=x+dx,z+dz
            if not(-646<=xx<=-565 and 735<=zz<=825):continue
            ground=height(xx,zz)
            for yy in (y,y-1):
                if yy<63 or abs(yy-ground)>6:continue
                q=xx,yy,zz;nc=c+1+abs(yy-ground)*.12
                if nc<cost.get(q,1e9):cost[q]=nc;parent[q]=p;heapq.heappush(queue,(nc+heuristic(q),nc,q))
    raise ValueError('No path found in the surveyed area')
