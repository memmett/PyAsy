
markers = '''

markroutine markskip(frame mark, int mod=1)
{
  if (mod > 0) {
    return new void(picture pic=currentpicture, frame f, path g) {
      for(int i=0; i <= length(g); ++i) {
          pair z=point(g,i);
          if (i % mod == 0) {
            add(pic, mark, z);
          }   
        }
      };
  }

  return new void(picture pic=currentpicture, frame f, path g) { };
}

frame star(int n, pen p, real angle=0)
{
  assert(n > 1);

  frame pic;
  
  real r = 1;
  real theta=pi/n;

  for (int i=0; i<n; ++i) {
    real s=sin(i*theta);
    real c=cos(i*theta);
    pair z1=(c,s);
    pair z2=(-c,-s);
    
    draw(pic, z1--z2, p);
  }

  return rotate(angle)*pic;
}

frame toframe(path g, pen p=black)
{
  frame pic;
  draw(pic, g, p);
  return pic;
}

'''
