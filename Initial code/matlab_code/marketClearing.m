function solution = marketClearing(qbid, pbid, direction, hour, demand)

        Nhour = 24;
        Nbid  = length(qbid);
        
        cplex = [];
        cplex = Cplex();
        cplex.DisplayFunc = 'off';
        cplex.Model.sense = 'minimize';
            
        % objective function
        obj = direction.*pbid;
        lb = zeros(Nbid,1);
        ub = qbid;
        cplex.addCols(obj,[],lb,ub);

        % dispatch constraint
        if (nargin == 4)
            AA=zeros(Nhour,Nbid);
            for h=1:24
                temp = find(hour==h);
                AA(h,temp')= direction(temp)';
            end
            AA = sparse(AA);
            rhs = zeros(Nhour,1);
            lhs = zeros(Nhour,1);
            cplex.addRows(lhs,AA,rhs);
        end
        if (nargin == 5)
            AA=zeros(2*Nhour,Nbid);
            for h=1:24
                temp = find((hour==h).*(direction == 1));
                AA(h,temp')= direction(temp)';
            end
            for h=1:24
                temp = find((hour==h).*(direction == -1));
                AA(Nhour+h,temp')= -direction(temp)';
            end
            AA = sparse(AA);
            rhs = [demand(:,1);demand(:,1)];
            lhs = [demand(:,1);demand(:,1)];
            cplex.addRows(lhs,AA,rhs);
        end
        
        % solution
        cplex.solve;
        solution = cplex.Solution;
        cplex.terminate;
        clear cplex;

end
