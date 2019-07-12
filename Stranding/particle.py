def _render(self):
    if self.num_particles == 0:
        return
    for i in range(self.num_particles):
        particle = self.particles[i]
        size = (self.texture.size[0] * particle.scale, self.texture.size[1] * particle.scale)
        if particle not in self.particles_dict:
            self.particles_dict[particle] = dict()
            color = particle.color[:]
            with self.canvas:
                self.particles_dict[particle]['color'] = Color(color[0], color[1], color[2], color[3])
                PushMatrix()
                self.particles_dict[particle]['translate'] = Translate()
                self.particles_dict[particle]['rotate'] = Rotate()
                self.particles_dict[particle]['rotate'].set(particle.rotation, 0, 0, 1)
                self.particles_dict[particle]['rect'] = Quad(texture=self.texture, points=(-size[0] * 0.5, -size[1] * 0.5, size[0] * 0.5, -size[1] * 0.5, size[0] * 0.5,  size[1] * 0.5, -size[0] * 0.5,  size[1] * 0.5))
                self.particles_dict[particle]['translate'].xy = (particle.x, particle.y)
                PopMatrix()
        else:
            self.particles_dict[particle]['rotate'].angle = particle.rotation
            self.particles_dict[particle]['translate'].xy = (particle.x, particle.y)
            self.particles_dict[particle]['color'].rgba = particle.color
            self.particles_dict[particle]['rect'].points = (-size[0] * 0.5, -size[1] * 0.5, size[0] * 0.5, -size[1] * 0.5, size[0] * 0.5,  size[1] * 0.5, -size[0] * 0.5,  size[1] * 0.5)
