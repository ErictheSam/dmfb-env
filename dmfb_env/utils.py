#!/usr/bin/python

import queue
from envs.dmfb import*

class OldRouter:
    """ An old router for DMFBs """
    def __init__(self, env):
        self.width = env.width
        self.length = env.length
        self.start = env.agt_sta
        self.end = env.agt_end
        self.modules = env.modules
        self.m_dist = self._computeDist()
        self.b_degrade = env.b_degrade
        self.m_health = env.m_health

    def getReward(self, b_path = False):
        path = [self.start]
        dist = self.m_dist[self.start[0]][self.start[1]]
        while dist > 1:
            old_dist = dist
            neighbors = self._getNeighbors(path[-1])
            for n in neighbors:
                if self.m_dist[n[0]][n[1]] ==\
                        dist - 1:
                    path.append(n)
                    dist = dist - 1
                    break
            if old_dist == dist:
                print('something wrong in getReward')
                print(path)
                print(self.m_dist)
                break
        if not self.b_degrade:
            reward = (len(path)-2) * (0.5) + 1.0
            if b_path:
                return len(path) - 1
            else:
                return reward
        else:
            num_steps = 0.
            for step in path[:-1]:
                prob = self.m_health[step[0]][step[1]]
                num_steps += 1. / prob
            reward = (len(path) - 2) * 0.5 + 1.0
            reward += (num_steps - len(path) + 2) * (-0.3)
            if b_path:
                return num_steps
            else:
                return reward

    def _computeDist(self):
        m_dist = np.zeros(
                shape = (self.width, self.length),
                dtype = np.uint8)
        q = queue.Queue()
        q.put(self.end)
        m_dist[self.end[0]][self.end[1]] = 1
        self._setModulesWithValue(m_dist, np.iinfo(np.uint8).max)
        while not q.empty():
            q, m_dist = self._updateQueue(q, m_dist)
        return m_dist

    def _setModulesWithValue(self, m_dist, v):
        for m in self.modules:
            for x in range(m.x_min, m.x_max + 1):
                for y in range(m.y_min, m.y_max + 1):
                    m_dist[y][x] = v
        return

    def _updateQueue(self, q, m_dist):
        head = q.get()
        dist = m_dist[head[0]][head[1]]
        neighbors = self._getNeighbors(head)
        for n in neighbors:
            if m_dist[n[0]][n[1]] == 0:
                q.put(n)
                m_dist[n[0]][n[1]] = dist + 1
        return q, m_dist

    def _getNeighbors(self, p):
        neighbors = [
                (p[0] - 1, p[1]),
                (p[0] + 1, p[1]),
                (p[0], p[1] - 1),
                (p[0], p[1] + 1)]
        return [n for n in neighbors if self._isWithinBoundary(n)]

    def _isWithinBoundary(self, p):
        if p[0] < self.width and p[0] >= 0 and\
                p[1] < self.length and p[1] >= 0:
            return True
        else:
            return False

