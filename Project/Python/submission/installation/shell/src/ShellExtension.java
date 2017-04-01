package org.nlogo.extensions.shell;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;
import java.util.ArrayList;
import org.nlogo.api.Argument;
import org.nlogo.api.Context;
import org.nlogo.api.DefaultCommand;
import org.nlogo.api.DefaultReporter;
import org.nlogo.api.ExtensionException;
import org.nlogo.api.LogoException;
import org.nlogo.api.PrimitiveManager;
import org.nlogo.api.Syntax;
import org.nlogo.nvm.ExtensionContext;

public class ShellExtension extends org.nlogo.api.DefaultClassManager {
    
    private static ProcessBuilder _pb;
    
	private static void initializeProcessBuilder(Context context){
		if(_pb == null) {
			_pb = new ProcessBuilder(new ArrayList<String>());
			_pb.redirectErrorStream(true);
			ExtensionContext ec = (ExtensionContext)context;
			try {
				_pb.directory(new java.io.File(ec.workspace().attachModelDir(".")));
			}
			catch(java.net.MalformedURLException e) {
				// oh well. I guess just default to whatever ProcessBuilder does
			}
		}
	}

    public void load (PrimitiveManager primManager) {
        primManager.addPrimitive("pwd", new GetWorkingDirectory());
        primManager.addPrimitive("cd", new SetWorkingDirectory());
        primManager.addPrimitive("getenv", new GetEnvironmentVariable());
        primManager.addPrimitive("setenv", new SetEnvironmentVariable());
        primManager.addPrimitive("exec", new Excec());
        primManager.addPrimitive("fork", new Fork());
    }
    
    public static class GetWorkingDirectory extends DefaultReporter {
        
        public Syntax getSyntax () {
            return Syntax.reporterSyntax(new int[] { }, Syntax.StringType());
        }
        
        public String getAgentClassString () {
            return "OTPL";
        }
        
        public Object report (Argument args[], Context context) throws ExtensionException, LogoException {
			initializeProcessBuilder(context);
            File dir = _pb.directory();
            if (dir != null) {
                return dir.toString();
            } else {
                return System.getProperty("user.dir");
            }
        }
    }

    public static class SetWorkingDirectory extends DefaultCommand {
        
        public Syntax getSyntax () {
            return Syntax.commandSyntax(new int[] { Syntax.StringType() });
        }
        
        public String getAgentClassString () {
            return "OTPL";
        }
        
        public void perform (Argument args[], Context context) throws ExtensionException, LogoException {
			initializeProcessBuilder(context);
            File newDir;
            String newDirName = args[0].getString();
            if (newDirName.startsWith("/") || newDirName.matches("^[a-zA-Z]:.*")) {
                // Parse as absolute path if it starts with a slash 
                // (Mac/Unix) or a drive letter and colon (Windows)
                newDir = new File(newDirName);
            } else {
                // Parse as relative to current directory
                File dir = _pb.directory();
                if (dir == null) {
                    dir = new File(System.getProperty("user.dir"));
                }
                newDir = new File(dir, newDirName);
            }
            try {
                newDir = newDir.getCanonicalFile();
            } catch (IOException e) {
                ExtensionException ex = new ExtensionException(e);
                ex.setStackTrace(e.getStackTrace());
                throw ex;
            }
            if (!newDir.exists()) {
                throw new ExtensionException("directory '"+newDir.toString()+"' does not exist");
            }
            _pb.directory(newDir);
        }
    }
    
    public static class SetEnvironmentVariable extends DefaultCommand {
        
        public Syntax getSyntax () {
            return Syntax.commandSyntax(new int[] { Syntax.StringType(), Syntax.StringType() });
        }
        
        public String getAgentClassString () {
            return "OTPL";
        }
        
        public void perform (Argument args[], Context context) throws ExtensionException, LogoException {
			initializeProcessBuilder(context);
            _pb.environment().put(args[0].getString(), args[1].getString());
        }
    }
    
    public static class GetEnvironmentVariable extends DefaultReporter {
        
        public Syntax getSyntax () {
            return Syntax.reporterSyntax(new int[] { Syntax.StringType() }, Syntax.StringType());
        }
        
        public String getAgentClassString () {
            return "OTPL";
        }
        
        public Object report (Argument args[], Context context) throws ExtensionException, LogoException {
			initializeProcessBuilder(context);
            String result = _pb.environment().get(args[0].getString());
            if (result != null) {
                return result;
            } else {
                return "";
            }
        }
    }
    
    public static class Excec extends DefaultReporter {
        
        public Syntax getSyntax () {
            return Syntax.reporterSyntax(new int[] { Syntax.StringType() | Syntax.RepeatableType() },
                                         Syntax.StringType(), 
                                         1);
        }
        
        public String getAgentClassString () {
            return "OTPL";
        }
        
        public Object report (Argument args[], Context context) throws ExtensionException, LogoException {
			initializeProcessBuilder(context);
            List<String> command = new ArrayList<String>(args.length);
            for (int i = 0; i < args.length; i += 1) {
                command.add(args[i].getString());
            }
            _pb.command(command);
            try {
                final Process process = _pb.start();
                final BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream()));
                final StringBuilder out = new StringBuilder();
                int c;
                while ((c = in.read()) >= 0) {
                    out.append((char)c);
                }
                return out.toString();
            } catch (IOException ioe) {
                ioe.printStackTrace();
                ExtensionException e = new ExtensionException(ioe.getMessage());
                e.setStackTrace(ioe.getStackTrace());
                throw e;
            }
        }
    }
    
    public static class Fork extends DefaultCommand {
        
        public Syntax getSyntax () {
            return Syntax.reporterSyntax(new int[] { Syntax.StringType() | Syntax.RepeatableType() }, 1);
        }
        
        public String getAgentClassString () {
            return "OTPL";
        }
        
        public void perform (Argument args[], Context context) throws ExtensionException, LogoException {
			initializeProcessBuilder(context);
            List<String> command = new ArrayList<String>(args.length);
            for (int i = 0; i < args.length; i += 1) {
                command.add(args[i].getString());
            }
            _pb.command(command);
            try {
                _pb.start();
            } catch (IOException ioe) {
                ioe.printStackTrace();
                ExtensionException e = new ExtensionException(ioe.getMessage());
                e.setStackTrace(ioe.getStackTrace());
                throw e;
            }
        }
    }
}
